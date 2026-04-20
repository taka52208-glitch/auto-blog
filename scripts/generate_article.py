"""
自動記事生成スクリプト
- トレンドキーワードを取得
- AIで記事を生成
- Hugoの記事ファイルとして保存
"""

import os
import json
import datetime
import random
import urllib.request
from pathlib import Path


def get_trending_keywords():
    """Googleトレンドから急上昇キーワードを取得"""
    url = "https://trends.google.co.jp/trending/rss?geo=JP"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode("utf-8")
            # 簡易XMLパース（title タグを抽出）
            keywords = []
            for line in data.split("<title>"):
                if "</title>" in line:
                    kw = line.split("</title>")[0].strip()
                    if kw and kw != "Daily Search Trends":
                        keywords.append(kw)
            return keywords[:10]
    except Exception as e:
        print(f"トレンド取得エラー: {e}")
        # フォールバック: 汎用キーワード
        return get_fallback_keywords()


def get_fallback_keywords():
    """トレンド取得失敗時のフォールバックキーワード"""
    topics = [
        "時短術", "節約方法", "副業", "AI活用", "健康習慣",
        "睡眠改善", "集中力", "ストレス解消", "自己投資", "朝活",
        "ミニマリスト", "作り置きレシピ", "掃除術", "防災グッズ",
        "スマホ活用術", "読書術", "筋トレ", "瞑想", "家計管理",
        "転職準備", "資格勉強", "プレゼン術", "人間関係", "習慣化"
    ]
    return random.sample(topics, 5)


def generate_article_with_ai(keyword):
    """Claude APIで記事を生成"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY が設定されていません")

    prompt = f"""以下のキーワードについて、SEOに最適化された日本語のブログ記事を書いてください。

キーワード: {keyword}

要件:
- タイトルはクリックしたくなるもの（32文字以内）
- 見出し(h2, h3)を適切に使う
- 1500〜2500文字程度
- 読者に価値を提供する内容
- 最後にまとめを入れる
- マークダウン形式で出力

出力形式:
---
title: "記事タイトル"
description: "メタディスクリプション（120文字以内）"
---

本文をここに書く
"""

    request_body = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["content"][0]["text"]


def save_article(content, keyword):
    """記事をHugoのコンテンツとして保存"""
    today = datetime.date.today().isoformat()
    # ファイル名を生成（日付 + キーワードのスラッグ）
    slug = keyword.replace(" ", "-").replace("　", "-").lower()
    filename = f"{today}-{slug}.md"

    # content/posts/ に保存
    posts_dir = Path(__file__).parent.parent / "content" / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    filepath = posts_dir / filename

    # frontmatter に日付を追加
    if "---" in content:
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]
            # 日付とカテゴリを追加
            frontmatter += f'\ndate: "{today}"\n'
            frontmatter += f'categories: ["トレンド"]\n'
            frontmatter += f'tags: ["{keyword}"]\n'
            content = f"---{frontmatter}---{body}"

    filepath.write_text(content, encoding="utf-8")
    print(f"記事を保存: {filepath}")
    return filepath


def main():
    print("=== 自動記事生成開始 ===")
    print(f"日時: {datetime.datetime.now()}")

    # 1. トレンドキーワード取得
    keywords = get_trending_keywords()
    print(f"取得キーワード: {keywords}")

    # 2. ランダムに1つ選択
    keyword = random.choice(keywords)
    print(f"選択キーワード: {keyword}")

    # 3. 記事生成
    print("記事生成中...")
    article = generate_article_with_ai(keyword)

    # 4. 保存
    save_article(article, keyword)

    print("=== 完了 ===")


if __name__ == "__main__":
    main()
