"""
自動記事生成スクリプト
- トレンドキーワードを取得
- Groq API（無料）で記事を生成
- Hugoの記事ファイルとして保存
"""

import os
import json
import datetime
import random
import urllib.request
import urllib.parse
from pathlib import Path


def get_trending_keywords():
    """Googleトレンドから急上昇キーワードを取得"""
    url = "https://trends.google.co.jp/trending/rss?geo=JP"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode("utf-8")
            keywords = []
            for line in data.split("<title>"):
                if "</title>" in line:
                    kw = line.split("</title>")[0].strip()
                    if kw and kw != "Daily Search Trends":
                        keywords.append(kw)
            return keywords[:10]
    except Exception as e:
        print(f"トレンド取得エラー: {e}")
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


def search_keyword_info(keyword):
    """WikipediaとGoogle検索でキーワードの正確な情報を取得"""
    info = ""

    # Wikipedia日本語版で検索
    try:
        wiki_url = f"https://ja.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(keyword)}"
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "AutoBlog/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            if "extract" in data:
                info += f"Wikipedia情報: {data['extract']}\n"
    except Exception as e:
        print(f"Wikipedia検索エラー: {e}")

    # DuckDuckGo Instant Answerで追加情報
    try:
        ddg_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(keyword)}&format=json&no_html=1"
        req = urllib.request.Request(ddg_url, headers={"User-Agent": "AutoBlog/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("Abstract"):
                info += f"概要: {data['Abstract']}\n"
            if data.get("RelatedTopics"):
                topics = [t.get("Text", "") for t in data["RelatedTopics"][:3] if isinstance(t, dict)]
                if topics:
                    info += f"関連情報: {'; '.join(topics)}\n"
    except Exception as e:
        print(f"DuckDuckGo検索エラー: {e}")

    return info if info else f"（{keyword}に関する事前情報は取得できませんでした）"


def generate_article_with_ai(keyword):
    """Groq API（無料）で記事を生成"""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY が設定されていません")

    # まずキーワードの正確な情報を取得
    print(f"キーワード情報を検索中: {keyword}")
    keyword_info = search_keyword_info(keyword)
    print(f"取得した情報: {keyword_info[:200]}")

    prompt = f"""あなたは人気ブロガーです。以下のトレンドキーワードについて、読者が「読んでよかった」と思える記事を書いてください。

キーワード: {keyword}

このキーワードについての事実情報:
{keyword_info}

## 記事の方針

1. まず「なぜ今このキーワードが話題なのか？」を考えて冒頭で触れる
2. 読者が検索する理由（知りたいこと）を3つ想定し、それぞれに答える
3. 他のサイトにはない「独自の切り口」を1つ入れる（例: 比較、ランキング、意外な事実、今後の予測）
4. 具体的なアクション（読者が次にやるべきこと）を最後に提示する

## 禁止事項
- Wikipediaのコピペのような羅列記事
- 「〜です。〜です。」の単調な繰り返し
- 確信のない事実や数字の捏造
- 当たり障りのないまとめ

## 文体
- 話しかけるような親しみやすい文体
- 「ぶっちゃけ」「実は」「意外と知られていないのが」などのフックを使う
- 短い文を多用してテンポよく

## フォーマット
- タイトル: 思わずクリックしたくなる（32文字以内）、数字や疑問形を活用
- 1500〜2500文字
- h2, h3で構造化
- マークダウン形式

出力形式:
---
title: "記事タイトル"
description: "メタディスクリプション（120文字以内）"
---

本文をここに書く
"""

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
    slug = keyword.replace(" ", "-").replace("　", "-").lower()
    filename = f"{today}-{slug}.md"

    posts_dir = Path(__file__).parent.parent / "content" / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    filepath = posts_dir / filename

    # frontmatter に日付を追加
    if "---" in content:
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]
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
