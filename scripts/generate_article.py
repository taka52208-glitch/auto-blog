"""
自動記事生成スクリプト（AIツール特化版）
- AIツール関連のロングテールキーワードを選定
- 比較・レビュー・使い方記事を生成
- アフィリエイトリンク付きで収益化
"""

import os
import json
import datetime
import random
import urllib.request
import urllib.parse
from pathlib import Path


# AIツール関連のロングテールキーワード（検索ボリュームあり・競合少ない）
ARTICLE_TEMPLATES = [
    # 比較系（成約率高い）
    {"keyword": "ChatGPT 無料版 有料版 違い", "type": "comparison"},
    {"keyword": "Claude ChatGPT 比較 どっち", "type": "comparison"},
    {"keyword": "Gemini ChatGPT 違い 2026", "type": "comparison"},
    {"keyword": "AI文章作成ツール おすすめ 無料", "type": "ranking"},
    {"keyword": "AI画像生成 無料 おすすめ 比較", "type": "ranking"},
    {"keyword": "AIライティングツール 比較 ブログ", "type": "ranking"},
    {"keyword": "AI翻訳 DeepL ChatGPT 比較", "type": "comparison"},
    {"keyword": "AI議事録ツール 無料 おすすめ", "type": "ranking"},
    {"keyword": "AIプレゼン作成ツール 比較", "type": "ranking"},
    {"keyword": "AI要約ツール 無料 使い方", "type": "howto"},
    # 使い方系（流入多い）
    {"keyword": "ChatGPT 使い方 初心者 始め方", "type": "howto"},
    {"keyword": "Claude 使い方 コツ プロンプト", "type": "howto"},
    {"keyword": "Midjourney 使い方 日本語 初心者", "type": "howto"},
    {"keyword": "Stable Diffusion 無料 使い方", "type": "howto"},
    {"keyword": "ChatGPT プロンプト 仕事 効率化", "type": "howto"},
    {"keyword": "AI副業 始め方 初心者 稼ぎ方", "type": "howto"},
    {"keyword": "ChatGPT ブログ記事 書き方 コツ", "type": "howto"},
    {"keyword": "AI 英語学習 おすすめ 方法", "type": "howto"},
    {"keyword": "ChatGPT Excel 活用 関数", "type": "howto"},
    {"keyword": "AI 動画編集 無料 おすすめ", "type": "ranking"},
    # 悩み解決系（検索意図が明確）
    {"keyword": "ChatGPT 料金 高い 節約方法", "type": "problem"},
    {"keyword": "AI 仕事 奪われる 対策 スキル", "type": "problem"},
    {"keyword": "ChatGPT 使えない 制限 代替", "type": "problem"},
    {"keyword": "AI ツール 多すぎ どれ 選ぶ", "type": "problem"},
    {"keyword": "Notion AI 料金 無料 代替", "type": "problem"},
    # 最新情報系
    {"keyword": "ChatGPT 最新機能 アップデート", "type": "news"},
    {"keyword": "Claude 新機能 できること", "type": "news"},
    {"keyword": "Google Gemini 最新 使い方", "type": "news"},
    {"keyword": "AI 最新ニュース まとめ", "type": "news"},
    {"keyword": "GPT-5 いつ 性能 予想", "type": "news"},
]


def get_published_keywords():
    """既に投稿済みのキーワードを取得して重複を避ける"""
    posts_dir = Path(__file__).parent.parent / "content" / "posts"
    published = set()
    if posts_dir.exists():
        for f in posts_dir.glob("*.md"):
            if f.name != ".gitkeep":
                published.add(f.stem.split("-", 3)[-1] if f.stem.count("-") >= 3 else f.stem)
    return published


def select_keyword():
    """未投稿のキーワードからランダムに1つ選択"""
    published = get_published_keywords()
    available = [t for t in ARTICLE_TEMPLATES if t["keyword"].replace(" ", "-").lower() not in published]
    if not available:
        # 全部投稿済みの場合はランダムに選ぶ（更新記事として）
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


def get_prompt_by_type(keyword, article_type, keyword_info):
    """記事タイプに応じたプロンプトを生成"""

    base_rules = """
## 文体ルール
- 話しかけるような親しみやすい口調
- 短い文でテンポよく
- 具体的な数字や例を入れる（料金は必ず記載）
- 読者が「へぇ」と思う意外な情報を1つ入れる
- 同じフレーズを繰り返さない（「ぶっちゃけ」「実は」は各1回まで）
- 各セクションに具体例や体験談風のエピソードを入れる

## SEOルール
- h2は3〜5個、h3は各h2の下に1〜3個
- キーワードを自然にh2に含める
- 冒頭100文字以内にキーワードを入れる
- 最後に「まとめ」と「次のアクション」

## 収益化
- 紹介するAIツールは実在する有名なものだけ（ChatGPT, Claude, Gemini, Midjourney, Canva AI, Notion AI, DeepL等）
- 各ツールの料金プランを正確に記載する
- 公式サイトへのリンクを[ツール名](公式URL)形式で入れる
- 「無料プランあり」「◯日間無料トライアル」などの情報を入れる

## 禁止
- 嘘の情報・確信のない数字
- 他サイトのコピペ感
- 「〜です。〜です。」の単調な繰り返し
- 1文が60文字を超える長文

## 出力形式
---
title: "タイトル（32文字以内・数字か疑問形入り）"
description: "メタディスクリプション（120文字以内）"
---

本文（2000〜3000文字）
"""

    if article_type == "comparison":
        specific = f"""
## 記事の構成
1. 結論を最初に書く（「○○な人は△△、□□な人は××がおすすめ」）
2. 比較表（料金・機能・使いやすさ）をマークダウンテーブルで
3. 各ツールの強み・弱みを具体的に
4. 用途別のおすすめを提示
5. まとめ
"""
    elif article_type == "ranking":
        specific = f"""
## 記事の構成
1. ランキング結果を冒頭で一覧表示
2. 各ツールを「おすすめ度」「料金」「特徴」で紹介
3. 選ぶ基準を3つ提示
4. 用途別おすすめ
5. まとめ
"""
    elif article_type == "howto":
        specific = f"""
## 記事の構成
1. この記事を読むとできるようになることを最初に書く
2. 手順をステップ形式（Step1, Step2...）で
3. よくある失敗と対策
4. 上級者向けのコツを1つ
5. まとめ
"""
    elif article_type == "problem":
        specific = f"""
## 記事の構成
1. 読者の悩みに共感する冒頭
2. 原因を簡潔に説明
3. 解決策を3つ提示（具体的に）
4. おすすめの代替ツール
5. まとめ
"""
    else:  # news
        specific = f"""
## 記事の構成
1. 最新情報のポイントを3行で
2. 何が変わったのか詳しく
3. ユーザーへの影響
4. 今後の予測
5. まとめ
"""

    return f"""あなたは月間10万PVのAIツールブロガーです。以下のキーワードで検索する読者に向けて、読んで「役に立った」と思える記事を書いてください。

キーワード: {keyword}
記事タイプ: {article_type}

参考情報:
{keyword_info}

{specific}
{base_rules}
"""


def generate_article_with_ai(keyword, article_type, keyword_info):
    """Groq API（無料）で記事を生成"""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY が設定されていません")

    prompt = get_prompt_by_type(keyword, article_type, keyword_info)

    request_body = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000,
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
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"Groq API Error {e.code}: {error_body}")
        raise


def save_article(content, keyword):
    """記事をHugoのコンテンツとして保存"""
    today = datetime.date.today().isoformat()
    slug = keyword.replace(" ", "-").lower()
    filename = f"{today}-{slug}.md"

    posts_dir = Path(__file__).parent.parent / "content" / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    filepath = posts_dir / filename

    # frontmatter処理
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
                tags = [k for k in keyword.split() if len(k) > 1][:3]
                frontmatter += f'tags: {json.dumps(tags, ensure_ascii=False)}\n'
            content = f"---{frontmatter}---{body}"
    else:
        tags = [k for k in keyword.split() if len(k) > 1][:3]
        content = f"""---
title: "{keyword}"
description: "{keyword}に関する最新情報をわかりやすく解説"
date: "{today}"
categories: ["AIツール"]
tags: {json.dumps(tags, ensure_ascii=False)}
---

{content}"""

    filepath.write_text(content, encoding="utf-8")
    print(f"記事を保存: {filepath}")
    return filepath


def main():
    print("=== AI Tools Lab 記事生成 ===")
    print(f"日時: {datetime.datetime.now()}")

    # 1. キーワード選定
    template = select_keyword()
    keyword = template["keyword"]
    article_type = template["type"]
    print(f"キーワード: {keyword}")
    print(f"記事タイプ: {article_type}")

    # 2. 関連情報検索
    print("関連情報を検索中...")
    keyword_info = search_keyword_info(keyword)

    # 3. 記事生成
    print("記事生成中...")
    article = generate_article_with_ai(keyword, article_type, keyword_info)

    # 4. 保存
    save_article(article, keyword)

    print("=== 完了 ===")


if __name__ == "__main__":
    main()
