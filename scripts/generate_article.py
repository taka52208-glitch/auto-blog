"""
自動記事生成スクリプト（v5 — 分割生成・レート制限対策）
- Groq無料枠（12,000 TPM）対策: 記事を前半・後半の2回に分けて生成
- 各APIコール間に65秒の待機を入れてTPMリセットを確保
- 運営者が実際に使っているツール・分野に絞ったキーワード
- 「体験者として書く」プロンプト
- 記事間の内部リンク自動生成
"""

import os
import json
import datetime
import random
import time
import urllib.request
import urllib.parse
from pathlib import Path


# ========================================
# アフィリエイトリンク設定（AIツール関連のみ）
# ========================================
AFFILIATE_LINKS = {
    "ChatGPT": {
        "url": "https://chat.openai.com",
        "text": "ChatGPT公式サイト",
        "note": "無料プランあり / Plus月額$20",
    },
    "Claude": {
        "url": "https://claude.ai",
        "text": "Claude公式サイト",
        "note": "無料プランあり / Pro月額$20",
    },
    "Cursor": {
        "url": "https://cursor.sh",
        "text": "Cursor公式サイト",
        "note": "無料プランあり / Pro月額$20",
    },
    "Gemini": {
        "url": "https://gemini.google.com",
        "text": "Gemini公式サイト",
        "note": "無料プランあり / Advanced月額2,900円",
    },
    "Perplexity": {
        "url": "https://www.perplexity.ai",
        "text": "Perplexity公式サイト",
        "note": "無料プランあり / Pro月額$20",
    },
    "Copilot": {
        "url": "https://copilot.microsoft.com",
        "text": "Microsoft Copilot公式サイト",
        "note": "無料プランあり / Pro月額3,200円",
    },
    "DeepL": {
        "url": "https://www.deepl.com",
        "text": "DeepL公式サイト",
        "note": "無料プランあり / Pro月額750円〜",
    },
    "Xserver": {
        "url": "https://px.a8.net/svt/ejp?a8mat=4B1RXW+6JSFM+CO4+3H2QRM",
        "text": "Xserver公式サイト",
        "note": "国内シェアNo.1 / 月額990円〜 / 10日間無料お試し",
    },
}


# ========================================
# キーワードリスト（運営者の体験分野に限定）
# ========================================
ARTICLE_TEMPLATES = [
    # ===== AIコーディング（主力分野） =====
    {"keyword": "Claude Code 使い方 実践 ガイド", "type": "howto"},
    {"keyword": "Claude Code Cursor 比較 どっち", "type": "comparison"},
    {"keyword": "AIコーディング 実務 使えるか リアル", "type": "howto"},
    {"keyword": "AI プログラミング 副業 始め方 実体験", "type": "howto"},
    {"keyword": "ChatGPT コーディング 限界 できないこと", "type": "problem"},
    {"keyword": "AIコーディング ハルシネーション 対策 実例", "type": "problem"},
    {"keyword": "GitHub Copilot Claude Code 比較 2026", "type": "comparison"},
    {"keyword": "AI LP制作 フリーランス 時短 方法", "type": "howto"},
    {"keyword": "AI 自動化ツール 開発 個人 始め方", "type": "howto"},
    {"keyword": "AIコーディング API連携 実装 コツ", "type": "howto"},

    # ===== ChatGPT / Claude 活用（毎日使っている） =====
    {"keyword": "ChatGPT Claude 使い分け 仕事 実践", "type": "comparison"},
    {"keyword": "ChatGPT 仕事効率化 具体例 テンプレ", "type": "howto"},
    {"keyword": "ChatGPT プロンプト 仕事 実例集 2026", "type": "howto"},
    {"keyword": "ChatGPT Excel CSV 自動化 実践", "type": "howto"},
    {"keyword": "Claude 長文処理 要約 仕事 活用", "type": "howto"},
    {"keyword": "ChatGPT メール 提案文 ビジネス 書き方", "type": "howto"},
    {"keyword": "AI 議事録 要約 無料 やり方", "type": "howto"},

    # ===== ブログ運営・収益化（実体験） =====
    {"keyword": "AIブログ 失敗談 量産 やめとけ", "type": "problem"},
    {"keyword": "Hugo GitHub Pages ブログ 始め方 無料", "type": "howto"},
    {"keyword": "ブログ 記事 一次情報 書き方 コツ", "type": "howto"},
    {"keyword": "AI アフィリエイト 始め方 初心者 注意点", "type": "howto"},
    {"keyword": "個人ブログ SEO 検索流入 増やし方 2026", "type": "howto"},

    # ===== AI副業・フリーランス（実体験） =====
    {"keyword": "AI 副業 フリーランス 始め方 実体験", "type": "howto"},
    {"keyword": "AI Web制作 案件 取り方 初心者", "type": "howto"},
    {"keyword": "ChatGPT 提案書 見積もり フリーランス 活用", "type": "howto"},
    {"keyword": "AI 業務自動化 ツール開発 受注 方法", "type": "howto"},

    # ===== AIコーディング追加 =====
    {"keyword": "Cursor 使い方 初心者 始め方 2026", "type": "howto"},
    {"keyword": "Claude Code ターミナル 開発 効率化", "type": "howto"},
    {"keyword": "AIコーディング セキュリティ 注意点 リスク", "type": "problem"},
    {"keyword": "AI コードレビュー 自動化 やり方", "type": "howto"},
    {"keyword": "AIコーディング デバッグ 使い方 実例", "type": "howto"},
    {"keyword": "Windsurf Cursor 比較 AIエディタ 2026", "type": "comparison"},
    {"keyword": "AI プログラミング 独学 ロードマップ 初心者", "type": "howto"},
    {"keyword": "ChatGPT API 使い方 Python 入門", "type": "howto"},

    # ===== ChatGPT / Claude 活用追加 =====
    {"keyword": "Claude 3.5 Sonnet 使い方 活用例", "type": "howto"},
    {"keyword": "ChatGPT 画像生成 DALL-E 使い方 実例", "type": "howto"},
    {"keyword": "AI 翻訳 DeepL ChatGPT 比較 精度", "type": "comparison"},
    {"keyword": "ChatGPT リサーチ 情報収集 仕事 コツ", "type": "howto"},
    {"keyword": "AI 文章校正 推敲 ツール おすすめ", "type": "howto"},
    {"keyword": "Perplexity AI 使い方 検索 違い", "type": "howto"},
    {"keyword": "ChatGPT プラグイン おすすめ 仕事 活用", "type": "howto"},
    {"keyword": "AI スライド プレゼン 自動作成 方法", "type": "howto"},

    # ===== ブログ・SEO追加 =====
    {"keyword": "ブログ アクセスゼロ 原因 対策 初心者", "type": "problem"},
    {"keyword": "AI SEOライティング コツ 上位表示 方法", "type": "howto"},
    {"keyword": "ブログ 収益化 アフィリエイト ASP おすすめ", "type": "howto"},
    {"keyword": "個人ブログ 続かない 継続 コツ 習慣化", "type": "problem"},

    # ===== AI副業・ビジネス追加 =====
    {"keyword": "AI 動画編集 副業 始め方 ツール", "type": "howto"},
    {"keyword": "ChatGPT ココナラ 出品 稼ぎ方 実例", "type": "howto"},
    {"keyword": "AI ノーコード アプリ開発 副業 始め方", "type": "howto"},
    {"keyword": "フリーランス ポートフォリオ 作り方 AI活用", "type": "howto"},
]

# ブログ記事に関連するキーワードのみXserverリンクを出す
KEYWORD_AFFILIATE_MAP = {
    "ブログ": ["Xserver"],
    "WordPress": ["Xserver"],
    "サーバー": ["Xserver"],
    "サイト": ["Xserver"],
}


def get_published_keywords():
    """既に投稿済みのキーワードを取得して重複を避ける"""
    posts_dir = Path(__file__).parent.parent / "content" / "posts"
    published = set()
    if posts_dir.exists():
        for f in posts_dir.glob("*.md"):
            if f.name != ".gitkeep":
                stem = f.stem
                parts = stem.split("-", 3)
                if len(parts) >= 4:
                    published.add(parts[3])
                else:
                    published.add(stem)
    return published


def get_published_articles():
    """投稿済み記事のタイトルとURLを取得（内部リンク用）"""
    posts_dir = Path(__file__).parent.parent / "content" / "posts"
    articles = []
    if posts_dir.exists():
        for f in posts_dir.glob("*.md"):
            if f.name == ".gitkeep":
                continue
            try:
                text = f.read_text(encoding="utf-8")
                title = ""
                slug = ""
                for line in text.split("\n"):
                    s = line.strip()
                    if s.startswith("title:") and not title:
                        title = line.split(":", 1)[1].strip().strip('"').strip("'")
                    elif s.startswith("slug:") and not slug:
                        slug = line.split(":", 1)[1].strip().strip('"').strip("'")
                if not slug:
                    import re as _re
                    slug = _re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem)
                if title:
                    articles.append({"title": title, "slug": slug})
            except Exception:
                pass
    return articles


def select_keyword():
    """未投稿のキーワードからランダムに1つ選択"""
    published = get_published_keywords()
    available = [t for t in ARTICLE_TEMPLATES if t["keyword"].replace(" ", "-").lower() not in published]
    if not available:
        print("全キーワード投稿済み。ランダムに1つ選択します。")
        available = ARTICLE_TEMPLATES
    return random.choice(available)


def search_keyword_info(keyword):
    """DuckDuckGoで関連情報を取得"""
    info = ""
    try:
        ddg_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(keyword)}&format=json&no_html=1"
        req = urllib.request.Request(ddg_url, headers={"User-Agent": "AutoBlog/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("Abstract"):
                info += f"{data['Abstract']}\n"
            if data.get("RelatedTopics"):
                topics = [t.get("Text", "") for t in data["RelatedTopics"][:5] if isinstance(t, dict)]
                if topics:
                    info += f"関連: {'; '.join(topics)}\n"
    except Exception as e:
        print(f"検索エラー: {e}")
    return info


def build_affiliate_section(keyword):
    """キーワードに関連するアフィリエイトリンク情報を生成"""
    links = []
    seen_urls = set()

    def add_link(tool_name):
        info = AFFILIATE_LINKS[tool_name]
        if info["url"] in seen_urls:
            return
        seen_urls.add(info["url"])
        links.append(f"- [{info['text']}]({info['url']}) — {info['note']}")

    # 1. キーワードベースのマッチ
    for trigger, tool_names in KEYWORD_AFFILIATE_MAP.items():
        if trigger in keyword:
            for name in tool_names:
                if name in AFFILIATE_LINKS:
                    add_link(name)

    # 2. ツール名の直接マッチ
    for tool_name in AFFILIATE_LINKS:
        if tool_name.lower() in keyword.lower():
            add_link(tool_name)

    return "\n".join(links)


def build_internal_links(current_keyword):
    """既存記事への内部リンクを生成（キーワード関連度順）"""
    articles = get_published_articles()
    if not articles:
        return ""

    current_words = set(current_keyword.lower().split())

    scored = []
    for a in articles:
        title_words = set(a["title"].lower().replace("【", " ").replace("】", " ").replace("｜", " ").split())
        slug_words = set(a["slug"].replace("-", " ").lower().split())
        all_words = title_words | slug_words
        overlap = len(current_words & all_words)
        scored.append((overlap, a))

    random.shuffle(scored)
    scored.sort(key=lambda x: x[0], reverse=True)

    selected = []
    for score, a in scored:
        if len(selected) >= 3:
            break
        if a["slug"] not in current_keyword.replace(" ", "-").lower():
            selected.append(a)

    links = []
    for a in selected:
        links.append(f"- [{a['title']}](/posts/{a['slug']}/)")
    return "\n".join(links)


def get_prompt(keyword, article_type, keyword_info):
    """記事生成プロンプト"""

    affiliate_section = build_affiliate_section(keyword)
    internal_links = build_internal_links(keyword)

    internal_links_instruction = ""
    if internal_links:
        internal_links_instruction = f"""
## 内部リンク（本文中に自然に組み込むこと）
以下の記事へのリンクを、関連する箇所で自然に挿入してください:
{internal_links}
"""

    type_instructions = {
        "comparison": """
## 記事の構成
1. 結論を最初に書く（「○○な人は△△、□□な人は××がおすすめ」）
2. 比較表（料金・機能・使いやすさ）をマークダウンテーブルで
3. 各ツールの強み・弱みを「自分が使って感じたこと」として書く
4. 用途別のおすすめを提示
""",
        "howto": """
## 記事の構成
1. この記事を読むとできるようになることを最初に書く
2. 手順をステップ形式（Step1, Step2...）で
3. 「自分がやったときにハマったポイント」を入れる
4. 上級者向けのコツを1つ
""",
        "problem": """
## 記事の構成
1. 読者の悩みに共感する冒頭（自分も同じ経験をした、という入り方）
2. 原因を簡潔に説明
3. 解決策を3つ提示（実際に試した結果を含める）
4. まとめ
""",
    }

    specific = type_instructions.get(article_type, type_instructions["howto"])

    return f"""あなたは、AIコーディングツール（Claude Code等）を使ってフリーランスでWeb制作・自動化ツール開発をしている個人ブロガーです。
ChatGPTとClaudeを毎日仕事で使い、Hugo + GitHub Pagesでブログを自分で構築・運用しています。

以下のキーワードで検索する読者に向けて、**自分が実際に使った体験に基づく記事**を書いてください。

キーワード: {keyword}
記事タイプ: {article_type}

参考情報:
{keyword_info}

{specific}

## 最重要ルール：体験者として書く
- 「筆者は〜」「私の場合は〜」「実際に使ってみると〜」のように、当事者の視点で書くこと
- 公式サイトの情報をまとめただけの記事にしない
- 「使ってみて良かった点」「期待外れだった点」「ハマったポイント」を必ず入れる
- 具体的な使用場面（LP制作、API連携、CSV整形、提案メール作成など）を例に出す

## 文体ルール
- 冒頭は毎回異なるパターンで書く（「〜と思ったことはありませんか？」は使わない）
- 冒頭直後に結論を書く
- 親しみやすい口調だが押し売り感を出さない
- 短い文でテンポよく（1文40文字以内を目安）
- 料金は正確に記載（確認できない場合は「公式サイトで要確認」）
- 同じフレーズを繰り返さない

## SEOルール
- タイトルにキーワードを含め、32文字以内
- h2は4〜6個
- 冒頭100文字以内にキーワードを入れる
- 比較対象がある場合はマークダウンテーブルを使う

## 収益化リンク（関連する場合のみ本文中に自然に挿入）
{affiliate_section}

{internal_links_instruction}

## 禁止
- 嘘の情報・確信のない数字・古い料金情報
- 出典のない統計データ（「約70%の企業が〜」のような根拠不明の数字）
- 存在しない法律・制度・サービスの捏造
- 同じ内容の繰り返し
- 内容の薄いセクション（各h2は最低150文字）

## 出力形式
---
title: "タイトル（32文字以内）"
description: "メタディスクリプション（80〜120文字）"
---

本文（**必ず3000文字以上**書くこと。2500文字未満は不合格。各h2セクションを300文字以上にして全体で3000〜4000文字を確保すること）
"""


def call_groq_api(prompt, max_tokens=4000, max_retries=5):
    """Groq APIを1回呼び出す（レート制限リトライ付き）"""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY が設定されていません")

    for attempt in range(max_retries):
        request_body = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "AutoBlog/1.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            print(f"Groq API Error {e.code}: {error_body}")
            if e.code == 429 and attempt < max_retries - 1:
                wait = 65
                print(f"レート制限。{wait}秒待機後リトライ ({attempt + 1}/{max_retries})...")
                time.sleep(wait)
                continue
            raise


def generate_article_with_ai(keyword, article_type, keyword_info):
    """Groq APIで記事を3分割生成（レート制限対策）"""

    affiliate_section = build_affiliate_section(keyword)
    internal_links = build_internal_links(keyword)

    today = datetime.date.today().isoformat()
    tags = json.dumps([k for k in keyword.split() if len(k) > 1][:5], ensure_ascii=False)
    slug = keyword.replace(' ', '-').lower()

    # --- Part 1: frontmatter + 導入文 + H2を1つ ---
    prompt_part1 = f"""あなたはAIコーディングツールでフリーランスWeb制作をしている個人ブロガーです。
ChatGPTとClaudeを毎日使い、Hugo + GitHub Pagesでブログを運用しています。

キーワード「{keyword}」で体験ベースの記事の**冒頭部分**を書いてください。

## 出力内容
1. frontmatter（---で囲む）
2. 導入文（200文字以上。結論を先に書く。冒頭にキーワードを含む）
3. 最初のH2セクション1つ（500文字以上。体験者視点で具体的に書く）

## ルール
- 「筆者は〜」「実際に〜」と当事者視点で書く
- 具体的な場面（LP制作、API連携、CSV整形など）を出す
- 短文でテンポよく。「〜と思ったことはありませんか？」は禁止

## 出力形式（これだけ出力）
---
title: "（32文字以内、キーワード含む）"
description: "（80〜120文字）"
date: "{today}"
categories: ["AIツール"]
tags: {tags}
slug: "{slug}"
---

（導入文）

## （H2見出し）

（本文500文字以上）"""

    print("  Part 1/3: 導入+H2×1を生成中...")
    part1 = call_groq_api(prompt_part1, max_tokens=3000)
    print(f"  Part 1 完了: {len(part1)}文字")

    print("  65秒待機...")
    time.sleep(65)

    # --- Part 2: H2を2つ ---
    part1_body = part1
    if "---" in part1:
        split = part1.split("---", 2)
        if len(split) >= 3:
            part1_body = split[2].strip()

    prompt_part2 = f"""以下のブログ記事の続きを書いてください。

キーワード: {keyword}

【ここまでの内容】
{part1_body[:800]}

## 出力内容
H2セクションを2つ書いてください（各500文字以上）。
前半と内容が被らないようにしてください。

## ルール
- 体験者視点を維持（「筆者は〜」「実際に〜」）
- 短文でテンポよく
- frontmatterや「---」は書かない。H2から始めること

## 出力形式（H2セクション2つだけ出力）
## （H2見出し1）

（本文500文字以上）

## （H2見出し2）

（本文500文字以上）"""

    print("  Part 2/3: H2×2を生成中...")
    part2 = call_groq_api(prompt_part2, max_tokens=3000)
    print(f"  Part 2 完了: {len(part2)}文字")

    print("  65秒待機...")
    time.sleep(65)

    # --- Part 3: まとめ + 内部リンク + アフィリエイト ---
    links_instruction = ""
    if internal_links:
        links_instruction = f"\n本文中に以下の関連記事リンクを自然に挿入:\n{internal_links}\n"

    aff_instruction = ""
    if affiliate_section:
        aff_instruction = f"\n関連する場合のみ自然に挿入:\n{affiliate_section}\n"

    prompt_part3 = f"""以下のブログ記事の最終パートを書いてください。

キーワード: {keyword}

## 出力内容
1. 実践的なH2セクション1つ（400文字以上。「始める手順」「注意点」「コツ」など実用的な内容）
2. まとめセクション（H2で「まとめ」。記事全体の要点を箇条書き3〜5個）
{links_instruction}{aff_instruction}
## ルール
- 体験者視点（「筆者は〜」「実際に〜」）
- 短文でテンポよく
- frontmatterや「---」は書かない

## 出力形式（本文のみ出力）
## （H2見出し）

（本文400文字以上）

## まとめ

（要点を箇条書き）"""

    print("  Part 3/3: まとめを生成中...")
    part3 = call_groq_api(prompt_part3, max_tokens=3000)
    print(f"  Part 3 完了: {len(part3)}文字")

    # --- 結合 ---
    combined = part1.rstrip() + "\n\n" + part2.strip() + "\n\n" + part3.strip()
    print(f"  結合後の総文字数: {len(combined)}文字")
    return combined


def save_article(content, keyword):
    """記事をHugoのコンテンツとして保存"""
    today = datetime.date.today().isoformat()
    slug = keyword.replace(" ", "-").lower()
    filename = f"{today}-{slug}.md"

    posts_dir = Path(__file__).parent.parent / "content" / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    filepath = posts_dir / filename

    if "---" in content:
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]
            if "date:" not in frontmatter:
                frontmatter += f'\ndate: "{today}"\n'
            if "categories:" not in frontmatter:
                frontmatter += f'categories: ["AIツール"]\n'
            if "tags:" not in frontmatter:
                tags = [k for k in keyword.split() if len(k) > 1][:5]
                frontmatter += f'tags: {json.dumps(tags, ensure_ascii=False)}\n'
            if "slug:" not in frontmatter:
                frontmatter += f'slug: "{slug}"\n'
            content = f"---{frontmatter}---{body}"
    else:
        tags = [k for k in keyword.split() if len(k) > 1][:5]
        content = f"""---
title: "{keyword}"
description: "{keyword}に関する実体験ベースの解説"
date: "{today}"
categories: ["AIツール"]
tags: {json.dumps(tags, ensure_ascii=False)}
slug: "{slug}"
---

{content}"""

    filepath.write_text(content, encoding="utf-8")
    print(f"記事を保存: {filepath}")
    return filepath


MIN_ARTICLE_LENGTH = 2000
MAX_RETRIES = 2


def validate_article(article):
    """記事の品質チェック"""
    body = article
    if "---" in article:
        parts = article.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]

    body_length = len(body.strip())
    if body_length < MIN_ARTICLE_LENGTH:
        return False, f"本文が短すぎます（{body_length}文字 < {MIN_ARTICLE_LENGTH}文字）"

    h2_count = body.count("\n## ")
    if h2_count < 3:
        return False, f"h2見出しが少なすぎます（{h2_count}個 < 3個）"

    return True, "OK"


def main():
    print("=== AI Tools Lab 記事生成 v5（分割生成） ===")
    print(f"日時: {datetime.datetime.now()}")

    template = select_keyword()
    keyword = template["keyword"]
    article_type = template["type"]
    print(f"キーワード: {keyword}")
    print(f"記事タイプ: {article_type}")

    print("関連情報を検索中...")
    keyword_info = search_keyword_info(keyword)

    article = None
    for attempt in range(MAX_RETRIES + 1):
        print(f"記事生成中...（試行 {attempt + 1}/{MAX_RETRIES + 1}）")
        article = generate_article_with_ai(keyword, article_type, keyword_info)

        is_valid, reason = validate_article(article)
        if is_valid:
            print("品質チェック: OK")
            break
        else:
            print(f"品質チェック: NG — {reason}")
            if attempt < MAX_RETRIES:
                print("再生成します...（65秒待機）")
                time.sleep(65)

    is_valid, reason = validate_article(article)
    if not is_valid:
        print(f"最終品質チェック: NG — {reason}")
        print("品質基準を満たさないため、記事を投稿しません。")
        return

    save_article(article, keyword)
    print("=== 完了 ===")


if __name__ == "__main__":
    main()
