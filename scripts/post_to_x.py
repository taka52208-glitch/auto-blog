"""
記事投稿後にX（Twitter）へ自動ポストするスクリプト
- 最新の記事からタイトルとURLを取得
- X API v2で投稿
"""

import os
import json
import hmac
import hashlib
import base64
import time
import urllib.request
import urllib.parse
import secrets
from pathlib import Path


SITE_URL = "https://taka52208-glitch.github.io/auto-blog"


def get_latest_article():
    """最新の記事ファイルからタイトルとスラグを取得"""
    posts_dir = Path(__file__).parent.parent / "content" / "posts"
    if not posts_dir.exists():
        return None

    files = sorted(posts_dir.glob("*.md"), reverse=True)
    for f in files:
        if f.name == ".gitkeep":
            continue
        text = f.read_text(encoding="utf-8")
        title = ""
        for line in text.split("\n"):
            if line.strip().startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"').strip("'")
                break
        if title:
            slug = f.stem
            return {"title": title, "slug": slug}
    return None


def percent_encode(s):
    """OAuth用のパーセントエンコード"""
    return urllib.parse.quote(str(s), safe="")


def create_oauth_signature(method, url, params, consumer_secret, token_secret):
    """OAuth 1.0a署名を生成"""
    sorted_params = "&".join(
        f"{percent_encode(k)}={percent_encode(v)}"
        for k, v in sorted(params.items())
    )
    base_string = f"{method}&{percent_encode(url)}&{percent_encode(sorted_params)}"
    signing_key = f"{percent_encode(consumer_secret)}&{percent_encode(token_secret)}"
    signature = hmac.new(
        signing_key.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(signature).decode("utf-8")


def post_to_x(text):
    """X API v2でポスト"""
    api_key = os.environ.get("X_API_KEY")
    api_secret = os.environ.get("X_API_SECRET")
    access_token = os.environ.get("X_ACCESS_TOKEN")
    access_secret = os.environ.get("X_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("X API credentials が設定されていません。スキップします。")
        return False

    url = "https://api.twitter.com/2/tweets"

    oauth_params = {
        "oauth_consumer_key": api_key,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA256",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }

    signature = create_oauth_signature(
        "POST", url, oauth_params, api_secret, access_secret
    )
    oauth_params["oauth_signature"] = signature

    auth_header = "OAuth " + ", ".join(
        f'{percent_encode(k)}="{percent_encode(v)}"'
        for k, v in sorted(oauth_params.items())
    )

    body = json.dumps({"text": text}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "User-Agent": "AutoBlog/1.0",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            print(f"Xに投稿成功: {result}")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"X API Error {e.code}: {error_body}")
        return False


def main():
    article = get_latest_article()
    if not article:
        print("記事が見つかりません")
        return

    article_url = f"{SITE_URL}/posts/{article['slug']}/"
    title = article["title"]

    # ポスト文面（140文字以内に収める）
    hashtags = "#AI #AIツール #ChatGPT"
    post_text = f"📝 新着記事\n\n{title}\n\n{article_url}\n\n{hashtags}"

    print(f"投稿内容:\n{post_text}")
    post_to_x(post_text)


if __name__ == "__main__":
    main()
