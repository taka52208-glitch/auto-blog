"""
記事一括再生成スクリプト
- 既存記事をバックアップして削除
- 改善プロンプトv4で N 本を再生成（日付は旧記事の範囲に分散）
- Groqレート制限対策で各生成間にウェイト

使い方:
  python scripts/batch_regenerate.py            # 40本生成
  python scripts/batch_regenerate.py 20         # 20本生成
  python scripts/batch_regenerate.py 5 --dry    # ドライラン（生成せず計画のみ表示）
"""

import os
import sys
import json
import time
import random
import shutil
import datetime
from pathlib import Path

# 既存ロジック再利用
from generate_article import (
    ARTICLE_TEMPLATES,
    search_keyword_info,
    generate_article_with_ai,
    validate_article,
    MAX_RETRIES,
)

POSTS_DIR = Path(__file__).parent.parent / "content" / "posts"
SLEEP_BETWEEN = 25  # 秒。Groq llama-3.3-70b 30 RPM対策（安全マージン込み）


def backup_and_clear_posts():
    """既存記事を _archive_<timestamp> に退避して posts を空にする"""
    if not POSTS_DIR.exists():
        return None, []

    existing = sorted(POSTS_DIR.glob("*.md"))
    if not existing:
        return None, []

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive = POSTS_DIR.parent / f"_archive_{ts}"
    archive.mkdir(parents=True, exist_ok=True)

    old_meta = []
    for f in existing:
        # 日付とslugを抽出（YYYY-MM-DD-slug.md）
        stem = f.stem
        parts = stem.split("-", 3)
        if len(parts) >= 4:
            old_meta.append({
                "date": "-".join(parts[:3]),
                "slug": parts[3],
                "filename": f.name,
            })
        shutil.move(str(f), str(archive / f.name))

    print(f"既存{len(existing)}本を退避: {archive}")
    return archive, old_meta


def pick_keywords(n, old_slugs):
    """ARTICLE_TEMPLATES からタイプ均等で n 本選ぶ。旧slugと完全一致は避ける"""
    by_type = {}
    for t in ARTICLE_TEMPLATES:
        by_type.setdefault(t["type"], []).append(t)

    for k in by_type:
        random.shuffle(by_type[k])

    selected = []
    types = list(by_type.keys())
    while len(selected) < n:
        progress = False
        for t in types:
            if by_type[t] and len(selected) < n:
                tmpl = by_type[t].pop()
                slug = tmpl["keyword"].replace(" ", "-").lower()
                # 旧slugとの完全一致は避ける（既存クロール記事との混乱回避）
                if slug in old_slugs:
                    continue
                selected.append(tmpl)
                progress = True
        if not progress:
            break

    # 不足分はフィルタなしで補充
    if len(selected) < n:
        remaining = [t for t in ARTICLE_TEMPLATES if t not in selected]
        random.shuffle(remaining)
        selected += remaining[: n - len(selected)]

    return selected[:n]


def assign_dates(keywords, old_meta):
    """各記事に日付を割り当てる。
    旧記事の日付範囲（最小〜最大）に均等分散させる。
    旧記事がなければ今日から逆算で1日2本配置。"""
    n = len(keywords)
    if old_meta:
        dates_sorted = sorted({m["date"] for m in old_meta})
        try:
            d_min = datetime.date.fromisoformat(dates_sorted[0])
            d_max = datetime.date.fromisoformat(dates_sorted[-1])
        except ValueError:
            d_min = datetime.date.today() - datetime.timedelta(days=n // 2)
            d_max = datetime.date.today()
    else:
        d_max = datetime.date.today()
        d_min = d_max - datetime.timedelta(days=max(n // 2, 1))

    span_days = (d_max - d_min).days
    if span_days < 1:
        span_days = max(n // 2, 1)
        d_min = d_max - datetime.timedelta(days=span_days)

    assigned = []
    for i, kw in enumerate(keywords):
        # i=0 → d_min, i=n-1 → d_max に均等に
        offset = round(i * span_days / max(n - 1, 1))
        d = d_min + datetime.timedelta(days=offset)
        assigned.append((kw, d.isoformat()))
    return assigned


def save_article_with_date(content, keyword, target_date):
    """指定日付で記事を保存（generate_article.save_article のフォーク版）"""
    slug = keyword.replace(" ", "-").lower()
    filename = f"{target_date}-{slug}.md"
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = POSTS_DIR / filename

    if "---" in content:
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]
            if "date:" not in frontmatter:
                frontmatter += f'\ndate: "{target_date}"\n'
            else:
                # 既存のdate行を target_date に置き換え
                new_lines = []
                replaced = False
                for line in frontmatter.split("\n"):
                    if line.strip().startswith("date:") and not replaced:
                        new_lines.append(f'date: "{target_date}"')
                        replaced = True
                    else:
                        new_lines.append(line)
                frontmatter = "\n".join(new_lines)
            if "categories:" not in frontmatter:
                frontmatter += 'categories: ["AIツール"]\n'
            if "tags:" not in frontmatter:
                tags = [k for k in keyword.split() if len(k) > 1][:5]
                frontmatter += f'tags: {json.dumps(tags, ensure_ascii=False)}\n'
            if "slug:" not in frontmatter:
                frontmatter += f'slug: "{slug}"\n'
            content = f"---{frontmatter}---{body}"
    else:
        tags = [k for k in keyword.split() if len(k) > 1][:5]
        content = (
            f'---\ntitle: "{keyword}"\n'
            f'description: "{keyword}に関する最新情報をわかりやすく解説"\n'
            f'date: "{target_date}"\n'
            f'categories: ["AIツール"]\n'
            f'tags: {json.dumps(tags, ensure_ascii=False)}\n'
            f'slug: "{slug}"\n---\n\n{content}'
        )

    filepath.write_text(content, encoding="utf-8")
    return filepath


def generate_one(template, target_date):
    keyword = template["keyword"]
    article_type = template["type"]
    print(f"\n--- {target_date} | {keyword} [{article_type}] ---")

    keyword_info = search_keyword_info(keyword)

    article = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            article = generate_article_with_ai(keyword, article_type, keyword_info)
        except Exception as e:
            print(f"  生成エラー (試行{attempt + 1}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(30)
                continue
            return None

        is_valid, reason = validate_article(article)
        if is_valid:
            path = save_article_with_date(article, keyword, target_date)
            print(f"  ✓ 保存: {path.name}")
            return path
        else:
            print(f"  ✗ 品質NG: {reason}")
            if attempt < MAX_RETRIES:
                time.sleep(15)

    print("  最大試行到達、スキップ")
    return None


def main():
    n = 40
    dry_run = False
    args = sys.argv[1:]
    for a in args:
        if a == "--dry":
            dry_run = True
        elif a.isdigit():
            n = int(a)

    print("=" * 50)
    print(f"バッチ再生成 開始: 目標={n}本 dry_run={dry_run}")
    print(f"日時: {datetime.datetime.now()}")
    print("=" * 50)

    if not os.environ.get("GROQ_API_KEY") and not dry_run:
        print("ERROR: GROQ_API_KEY 未設定")
        sys.exit(1)

    # 1. バックアップ
    if not dry_run:
        archive, old_meta = backup_and_clear_posts()
    else:
        existing = sorted(POSTS_DIR.glob("*.md")) if POSTS_DIR.exists() else []
        old_meta = []
        for f in existing:
            stem = f.stem
            parts = stem.split("-", 3)
            if len(parts) >= 4:
                old_meta.append({"date": "-".join(parts[:3]), "slug": parts[3]})

    old_slugs = {m["slug"] for m in old_meta}
    print(f"旧記事: {len(old_meta)}本")

    # 2. キーワード選定
    keywords = pick_keywords(n, old_slugs)
    print(f"選定: {len(keywords)}本")

    # 3. 日付割当
    plan = assign_dates(keywords, old_meta)

    print("\n--- 生成計画 ---")
    for kw, d in plan:
        print(f"  {d} | {kw['keyword']} ({kw['type']})")

    if dry_run:
        print("\n[DRY RUN] 終了")
        return

    # 4. 生成実行
    success = 0
    failed = []
    for i, (tmpl, target_date) in enumerate(plan, 1):
        print(f"\n[{i}/{len(plan)}]")
        result = generate_one(tmpl, target_date)
        if result:
            success += 1
        else:
            failed.append(tmpl["keyword"])

        if i < len(plan):
            print(f"  ({SLEEP_BETWEEN}秒待機)")
            time.sleep(SLEEP_BETWEEN)

    print("\n" + "=" * 50)
    print(f"完了: 成功 {success}/{len(plan)}")
    if failed:
        print(f"失敗キーワード: {failed}")
    print("=" * 50)

    if success < n // 2:
        print("ERROR: 成功率が低すぎます。終了コード1で終了します。")
        sys.exit(1)


if __name__ == "__main__":
    main()
