"""
自動記事生成スクリプト（AIツール特化版 v2）
- 100以上のロングテールキーワード
- アフィリエイトリンク自動挿入
- 記事間の内部リンク自動生成
- 1日2記事対応
"""

import os
import json
import datetime
import random
import urllib.request
import urllib.parse
from pathlib import Path


# ========================================
# アフィリエイトリンク設定
# ========================================
# ASP登録後に実際のアフィリエイトリンクに差し替えてください
# A8.net / もしもアフィリエイト / バリューコマース 等
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
    "Gemini": {
        "url": "https://gemini.google.com",
        "text": "Gemini公式サイト",
        "note": "無料プランあり / Advanced月額2,900円",
    },
    "Midjourney": {
        "url": "https://www.midjourney.com",
        "text": "Midjourney公式サイト",
        "note": "Basic月額$10〜",
    },
    "Stable Diffusion": {
        "url": "https://stability.ai",
        "text": "Stability AI公式サイト",
        "note": "オープンソース無料 / DreamStudio有料",
    },
    "Canva": {
        "url": "https://www.canva.com",
        "text": "Canva公式サイト",
        "note": "無料プランあり / Pro月額1,000円",
    },
    "Notion AI": {
        "url": "https://www.notion.so",
        "text": "Notion公式サイト",
        "note": "AI機能は月額$10の追加オプション",
    },
    "DeepL": {
        "url": "https://www.deepl.com",
        "text": "DeepL公式サイト",
        "note": "無料プランあり / Pro月額750円〜",
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
    "Adobe Firefly": {
        "url": "https://firefly.adobe.com",
        "text": "Adobe Firefly公式サイト",
        "note": "無料枠あり / Creative Cloud契約で利用可",
    },
    "Jasper": {
        "url": "https://www.jasper.ai",
        "text": "Jasper公式サイト",
        "note": "Creator月額$49〜 / 7日間無料トライアル",
    },
    "Grammarly": {
        "url": "https://www.grammarly.com",
        "text": "Grammarly公式サイト",
        "note": "無料プランあり / Premium月額$12",
    },
    "Descript": {
        "url": "https://www.descript.com",
        "text": "Descript公式サイト",
        "note": "無料プランあり / Pro月額$24",
    },
    "Runway": {
        "url": "https://runwayml.com",
        "text": "Runway公式サイト",
        "note": "無料枠あり / Standard月額$12",
    },
    "ElevenLabs": {
        "url": "https://elevenlabs.io",
        "text": "ElevenLabs公式サイト",
        "note": "無料枠あり / Starter月額$5",
    },
    "Cursor": {
        "url": "https://cursor.sh",
        "text": "Cursor公式サイト",
        "note": "無料プランあり / Pro月額$20",
    },
    "Otter.ai": {
        "url": "https://otter.ai",
        "text": "Otter.ai公式サイト",
        "note": "無料プランあり / Pro月額$16.99",
    },
    "DALL-E": {
        "url": "https://openai.com/dall-e-3",
        "text": "DALL-E公式サイト",
        "note": "ChatGPT Plus内で利用可",
    },
    "Suno": {
        "url": "https://suno.com",
        "text": "Suno公式サイト",
        "note": "無料枠あり / Pro月額$10",
    },
    "Xserver": {
        "url": "https://px.a8.net/svt/ejp?a8mat=4B1RXW+6JSFM+CO4+3H2QRM",
        "text": "Xserver公式サイト",
        "note": "国内シェアNo.1 / 月額990円〜 / 10日間無料お試し",
    },
    "R4CAREER": {
        "url": "https://px.a8.net/svt/ejp?a8mat=457CWF+5Q0036+576C+5YJRM",
        "text": "R4CAREER 名古屋の転職エージェント",
        "note": "東海3県特化 / 無料相談あり / ぴったり転職",
    },
    "合宿免許受付センター": {
        "url": "https://px.a8.net/svt/ejp?a8mat=3T2LTO+AYQEUQ+2C9M+61RI9",
        "text": "合宿免許受付センター",
        "note": "最短14日で卒業 / 全国の教習所から選べる / 食事・宿泊込み",
    },
    "マッチングフォト": {
        "url": "https://px.a8.net/svt/ejp?a8mat=3NEIAG+4EDBOY+4MM2+5YJRM",
        "text": "マッチングフォト",
        "note": "プロ撮影 / マッチングアプリ特化 / 全国対応",
    },
    "楽天トラベル": {
        "url": "https://rpx.a8.net/svt/ejp?a8mat=3BIB16+BQPSAA+2HOM+6I9N5&rakuten=y&a8ejpredirect=http%3A%2F%2Fhb.afl.rakuten.co.jp%2Fhgc%2F0eb4779e.5d30c5ba.0eb4779f.b871e4e3%2Fa20072855679_3BIB16_BQPSAA_2HOM_6I9N5%3Fpc%3Dhttp%253A%252F%252Ftravel.rakuten.co.jp%252F%26m%3Dhttp%253A%252F%252Ftravel.rakuten.co.jp%252F",
        "text": "楽天トラベル",
        "note": "ホテル・旅館予約 / ポイント貯まる / クーポン多数",
    },
}


# ========================================
# キーワードリスト（100以上）
# ========================================
ARTICLE_TEMPLATES = [
    # ===== 比較系（成約率高い） =====
    {"keyword": "ChatGPT 無料版 有料版 違い", "type": "comparison"},
    {"keyword": "Claude ChatGPT 比較 どっち", "type": "comparison"},
    {"keyword": "Gemini ChatGPT 違い 2026", "type": "comparison"},
    {"keyword": "AI翻訳 DeepL ChatGPT 比較", "type": "comparison"},
    {"keyword": "Perplexity ChatGPT 違い 検索", "type": "comparison"},
    {"keyword": "Copilot ChatGPT 比較 無料", "type": "comparison"},
    {"keyword": "Claude Gemini 比較 性能", "type": "comparison"},
    {"keyword": "Midjourney DALL-E 比較 画像生成", "type": "comparison"},
    {"keyword": "Stable Diffusion Midjourney 違い", "type": "comparison"},
    {"keyword": "Notion AI ChatGPT 使い分け", "type": "comparison"},
    {"keyword": "Grammarly DeepL 英語 比較", "type": "comparison"},
    {"keyword": "Jasper ChatGPT ライティング 比較", "type": "comparison"},
    {"keyword": "Cursor GitHub Copilot 比較 プログラミング", "type": "comparison"},
    {"keyword": "Adobe Firefly Midjourney 比較 商用利用", "type": "comparison"},
    {"keyword": "ElevenLabs VOICEVOX 比較 音声AI", "type": "comparison"},

    # ===== ランキング系（流入多い） =====
    {"keyword": "AI文章作成ツール おすすめ 無料", "type": "ranking"},
    {"keyword": "AI画像生成 無料 おすすめ 比較", "type": "ranking"},
    {"keyword": "AIライティングツール 比較 ブログ", "type": "ranking"},
    {"keyword": "AI議事録ツール 無料 おすすめ", "type": "ranking"},
    {"keyword": "AIプレゼン作成ツール 比較", "type": "ranking"},
    {"keyword": "AI動画編集 無料 おすすめ", "type": "ranking"},
    {"keyword": "AIコーディング ツール おすすめ 2026", "type": "ranking"},
    {"keyword": "AI音声読み上げ 無料 おすすめ", "type": "ranking"},
    {"keyword": "AI翻訳ツール おすすめ ランキング", "type": "ranking"},
    {"keyword": "AI作曲 無料 おすすめ ツール", "type": "ranking"},
    {"keyword": "AIチャットボット おすすめ ビジネス", "type": "ranking"},
    {"keyword": "AI履歴書 作成ツール おすすめ", "type": "ranking"},
    {"keyword": "AIデザインツール 無料 おすすめ", "type": "ranking"},
    {"keyword": "AI要約ツール 無料 おすすめ", "type": "ranking"},
    {"keyword": "AIスライド作成 自動 おすすめ", "type": "ranking"},
    {"keyword": "AI SEOツール おすすめ ブログ", "type": "ranking"},
    {"keyword": "AIメール作成 ツール おすすめ", "type": "ranking"},
    {"keyword": "AI Excel分析 ツール おすすめ", "type": "ranking"},
    {"keyword": "AI SNS運用 ツール おすすめ", "type": "ranking"},
    {"keyword": "AI 自動字幕 ツール 無料", "type": "ranking"},

    # ===== 使い方系（流入多い） =====
    {"keyword": "ChatGPT 使い方 初心者 始め方", "type": "howto"},
    {"keyword": "Claude 使い方 コツ プロンプト", "type": "howto"},
    {"keyword": "Midjourney 使い方 日本語 初心者", "type": "howto"},
    {"keyword": "Stable Diffusion 無料 使い方", "type": "howto"},
    {"keyword": "ChatGPT プロンプト 仕事 効率化", "type": "howto"},
    {"keyword": "AI副業 始め方 初心者 稼ぎ方", "type": "howto"},
    {"keyword": "ChatGPT ブログ記事 書き方 コツ", "type": "howto"},
    {"keyword": "AI 英語学習 おすすめ 方法", "type": "howto"},
    {"keyword": "ChatGPT Excel 活用 関数", "type": "howto"},
    {"keyword": "AI要約ツール 無料 使い方", "type": "howto"},
    {"keyword": "Perplexity 使い方 検索 コツ", "type": "howto"},
    {"keyword": "Canva AI 使い方 デザイン 初心者", "type": "howto"},
    {"keyword": "Notion AI 使い方 活用術", "type": "howto"},
    {"keyword": "ChatGPT API 使い方 初心者", "type": "howto"},
    {"keyword": "Gemini 使い方 Google 連携", "type": "howto"},
    {"keyword": "ChatGPT プラグイン おすすめ 使い方", "type": "howto"},
    {"keyword": "AI 議事録 自動作成 やり方", "type": "howto"},
    {"keyword": "ChatGPT 画像生成 DALL-E 使い方", "type": "howto"},
    {"keyword": "AI 文章校正 やり方 無料", "type": "howto"},
    {"keyword": "ChatGPT スマホ アプリ 使い方", "type": "howto"},
    {"keyword": "Runway 動画生成 使い方 初心者", "type": "howto"},
    {"keyword": "Suno AI 作曲 使い方 日本語", "type": "howto"},
    {"keyword": "ElevenLabs 音声クローン 使い方", "type": "howto"},
    {"keyword": "Cursor AI プログラミング 使い方", "type": "howto"},
    {"keyword": "Descript 動画編集 文字起こし 使い方", "type": "howto"},

    # ===== 料金・節約系（成約直結） =====
    {"keyword": "ChatGPT Plus 料金 元取れる", "type": "problem"},
    {"keyword": "ChatGPT 料金 高い 節約方法", "type": "problem"},
    {"keyword": "Notion AI 料金 無料 代替", "type": "problem"},
    {"keyword": "Midjourney 料金プラン おすすめ", "type": "problem"},
    {"keyword": "Claude Pro 料金 価値 レビュー", "type": "problem"},
    {"keyword": "AI ツール 月額 節約 まとめ", "type": "problem"},
    {"keyword": "ChatGPT Team 料金 個人 お得", "type": "problem"},
    {"keyword": "Gemini Advanced 料金 必要か", "type": "problem"},
    {"keyword": "AI ツール 無料で使う 方法 まとめ", "type": "problem"},
    {"keyword": "Copilot Pro 料金 契約すべきか", "type": "problem"},
    {"keyword": "Adobe Firefly 料金 無料 範囲", "type": "problem"},
    {"keyword": "Jasper AI 料金 高い 代替", "type": "problem"},
    {"keyword": "Perplexity Pro 料金 無料 違い", "type": "problem"},

    # ===== 悩み解決系（検索意図が明確） =====
    {"keyword": "AI 仕事 奪われる 対策 スキル", "type": "problem"},
    {"keyword": "ChatGPT 使えない 制限 代替", "type": "problem"},
    {"keyword": "AI ツール 多すぎ どれ 選ぶ", "type": "problem"},
    {"keyword": "ChatGPT 回答 嘘 ハルシネーション 対策", "type": "problem"},
    {"keyword": "AI 著作権 問題 商用利用 注意点", "type": "problem"},
    {"keyword": "ChatGPT セキュリティ 会社 利用 注意", "type": "problem"},
    {"keyword": "AI 画像生成 著作権 問題 安全", "type": "problem"},
    {"keyword": "ChatGPT 遅い 重い 対処法", "type": "problem"},
    {"keyword": "AI ライティング バレる 対策", "type": "problem"},
    {"keyword": "AI 副業 詐欺 見分け方 注意", "type": "problem"},

    # ===== 仕事活用系（ビジネスパーソン狙い） =====
    {"keyword": "ChatGPT 仕事 活用例 ビジネス", "type": "howto"},
    {"keyword": "AI 業務効率化 ツール 事例", "type": "howto"},
    {"keyword": "ChatGPT メール 文章 ビジネス テンプレ", "type": "howto"},
    {"keyword": "AI 企画書 作成 プロンプト", "type": "howto"},
    {"keyword": "ChatGPT マーケティング 活用 方法", "type": "howto"},
    {"keyword": "AI データ分析 初心者 ツール", "type": "howto"},
    {"keyword": "ChatGPT プレゼン資料 作り方", "type": "howto"},
    {"keyword": "AI 営業 活用 メール 商談", "type": "howto"},
    {"keyword": "ChatGPT 報告書 作成 テンプレ", "type": "howto"},
    {"keyword": "AI 人事 採用 活用 事例", "type": "howto"},

    # ===== 副業・稼ぐ系（高単価） =====
    {"keyword": "AI 副業 おすすめ 2026 稼ぐ", "type": "howto"},
    {"keyword": "ChatGPT ブログ 稼ぐ 方法 月5万", "type": "howto"},
    {"keyword": "AIブログ 始め方 WordPress サーバー おすすめ", "type": "howto"},
    {"keyword": "AI 転職 キャリアチェンジ 未経験 おすすめ", "type": "howto"},
    {"keyword": "AI時代 転職 スキル 将来性", "type": "problem"},
    {"keyword": "AI イラスト 販売 稼ぎ方", "type": "howto"},
    {"keyword": "AI ライター 副業 始め方 単価", "type": "howto"},
    {"keyword": "AI 動画編集 副業 稼ぐ 方法", "type": "howto"},
    {"keyword": "AI プログラミング 副業 未経験", "type": "howto"},
    {"keyword": "AI 翻訳 副業 在宅 収入", "type": "howto"},
    {"keyword": "ChatGPT コンテンツ販売 やり方", "type": "howto"},
    {"keyword": "AI 写真加工 副業 稼ぐ", "type": "howto"},
    {"keyword": "AI ナレーション 副業 始め方", "type": "howto"},

    # ===== 最新情報系 =====
    {"keyword": "ChatGPT 最新機能 アップデート", "type": "news"},
    {"keyword": "Claude 新機能 できること", "type": "news"},
    {"keyword": "Google Gemini 最新 使い方", "type": "news"},
    {"keyword": "AI 最新ニュース まとめ", "type": "news"},
    {"keyword": "GPT-5 いつ 性能 予想", "type": "news"},
    {"keyword": "AI 規制 法律 日本 最新", "type": "news"},
    {"keyword": "OpenAI 最新 ニュース まとめ", "type": "news"},
    {"keyword": "Anthropic Claude 最新 アップデート", "type": "news"},
    {"keyword": "AI 業界 トレンド 2026 予測", "type": "news"},
    {"keyword": "Google AI 新サービス まとめ", "type": "news"},

    # ===== 学生・学習系 =====
    {"keyword": "AI レポート 書き方 大学生 注意", "type": "howto"},
    {"keyword": "ChatGPT 勉強 活用法 学生", "type": "howto"},
    {"keyword": "AI プログラミング学習 独学 おすすめ", "type": "howto"},
    {"keyword": "ChatGPT 英会話 練習 無料 方法", "type": "howto"},
    {"keyword": "AI 資格勉強 活用 おすすめ", "type": "howto"},

    # ===== 収益直結系（Xserver/R4CAREER成約狙い） =====
    {"keyword": "AIブログ 収益化 月5万 ロードマップ", "type": "howto"},
    {"keyword": "AI副業ブログ WordPress 始め方 完全ガイド", "type": "howto"},
    {"keyword": "AIアフィリエイト 稼ぐ サイト 作り方", "type": "howto"},
    {"keyword": "ChatGPT ブログ 自動化 収益 仕組み", "type": "howto"},
    {"keyword": "レンタルサーバー 比較 ブログ初心者 おすすめ", "type": "ranking"},
    {"keyword": "Xserver ConoHa 比較 ブログ どっち", "type": "comparison"},
    {"keyword": "AI 転職 未経験 成功する 方法", "type": "howto"},
    {"keyword": "AIエンジニア 転職 年収 ロードマップ", "type": "howto"},
    {"keyword": "AI人材 求人 未経験OK 探し方", "type": "howto"},
    {"keyword": "ChatGPT 転職活動 履歴書 職務経歴書 書き方", "type": "howto"},
    {"keyword": "AI時代 おすすめ 資格 スキル 転職に有利", "type": "ranking"},
    {"keyword": "プログラミング AI 独学 副業 月10万", "type": "howto"},
    {"keyword": "AI Webライター 始め方 月3万 稼ぐ", "type": "howto"},
    {"keyword": "AI 自動収益 ブログ 不労所得 方法", "type": "howto"},
    {"keyword": "AIツール 組み合わせ 副業 効率化 戦略", "type": "howto"},
    {"keyword": "AI 在宅ワーク おすすめ 主婦 副業", "type": "ranking"},
    {"keyword": "AI写真 プロフィール写真 撮影 おすすめ", "type": "ranking"},
    {"keyword": "マッチングアプリ 写真 撮り方 AI加工 コツ", "type": "howto"},
]


def get_published_keywords():
    """既に投稿済みのキーワードを取得して重複を避ける"""
    posts_dir = Path(__file__).parent.parent / "content" / "posts"
    published = set()
    if posts_dir.exists():
        for f in posts_dir.glob("*.md"):
            if f.name != ".gitkeep":
                # ファイル名からキーワード部分を抽出
                stem = f.stem
                # YYYY-MM-DD-keyword の形式
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
                for line in text.split("\n"):
                    if line.strip().startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"').strip("'")
                        break
                if title:
                    slug = f.stem
                    articles.append({"title": title, "slug": slug})
            except Exception:
                pass
    return articles


def select_keyword():
    """未投稿のキーワードからランダムに1つ選択"""
    published = get_published_keywords()
    available = [t for t in ARTICLE_TEMPLATES if t["keyword"].replace(" ", "-").lower() not in published]
    if not available:
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


KEYWORD_AFFILIATE_MAP = {
    # 転職・キャリア系 → R4CAREER（高単価）
    "転職": ["R4CAREER"],
    "キャリア": ["R4CAREER"],
    "仕事 奪われる": ["R4CAREER"],
    "AI時代 転職": ["R4CAREER"],
    "未経験": ["R4CAREER"],
    # ブログ・サイト運営系 → Xserver（高単価・成約しやすい）
    "ブログ": ["Xserver"],
    "WordPress": ["Xserver"],
    "サーバー": ["Xserver"],
    "副業": ["Xserver"],
    "在宅": ["Xserver"],
    "稼ぐ": ["Xserver"],
    "コンテンツ販売": ["Xserver"],
    # 写真・画像系 → マッチングフォト
    "画像生成": ["マッチングフォト"],
    "写真": ["マッチングフォト"],
    "AI イラスト": ["マッチングフォト"],
    "デザイン": ["マッチングフォト"],
}



# A8.net等の実際にコミッションが発生するアフィリエイトリンク
PAID_AFFILIATE_KEYS = ["Xserver", "R4CAREER", "合宿免許受付センター", "マッチングフォト", "楽天トラベル"]


def build_affiliate_section(keyword):
    """キーワードに関連するアフィリエイトリンク情報を生成（報酬リンク優先）"""
    links = []
    seen_urls = set()

    def add_link(tool_name):
        info = AFFILIATE_LINKS[tool_name]
        if info["url"] in seen_urls:
            return
        seen_urls.add(info["url"])
        links.append(f"- [{info['text']}]({info['url']}) — {info['note']}")

    # 1. キーワードベースのマッチ（ASP案件優先）
    for trigger, tool_names in KEYWORD_AFFILIATE_MAP.items():
        if trigger in keyword:
            for name in tool_names:
                if name in AFFILIATE_LINKS:
                    add_link(name)

    # 2. ツール名の直接マッチ
    for tool_name in AFFILIATE_LINKS:
        if tool_name.lower() in keyword.lower():
            add_link(tool_name)

    # 3. フォールバック: ASP案件（報酬が出るリンク）を優先的に追加
    if len(links) < 2:
        paid_candidates = [k for k in PAID_AFFILIATE_KEYS if k not in seen_urls]
        random.shuffle(paid_candidates)
        for key in paid_candidates:
            if key in AFFILIATE_LINKS:
                add_link(key)
            if len(links) >= 3:
                break

    # 4. それでも足りなければ関連ツールを追加
    if len(links) < 2:
        candidates = [k for k in AFFILIATE_LINKS if AFFILIATE_LINKS[k]["url"] not in seen_urls]
        for tool_name in random.sample(candidates, min(3, len(candidates))):
            add_link(tool_name)
            if len(links) >= 3:
                break

    return "\n".join(links)


def build_internal_links(current_keyword):
    """既存記事への内部リンクを生成（キーワード関連度順）"""
    articles = get_published_articles()
    if not articles:
        return ""

    current_words = set(current_keyword.lower().split())

    # 各記事との関連度スコアを計算
    scored = []
    for a in articles:
        title_words = set(a["title"].lower().replace("【", " ").replace("】", " ").replace("｜", " ").split())
        slug_words = set(a["slug"].replace("-", " ").lower().split())
        all_words = title_words | slug_words
        overlap = len(current_words & all_words)
        scored.append((overlap, a))

    # 関連度順にソート（同スコアならランダム）
    random.shuffle(scored)
    scored.sort(key=lambda x: x[0], reverse=True)

    # 上位3記事（ただし完全一致の自分自身は除く）
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


def get_prompt_by_type(keyword, article_type, keyword_info):
    """記事タイプに応じたプロンプトを生成"""

    affiliate_section = build_affiliate_section(keyword)
    internal_links = build_internal_links(keyword)

    internal_links_instruction = ""
    if internal_links:
        internal_links_instruction = f"""
## 内部リンク（本文中に自然に組み込むこと）
以下の記事へのリンクを、関連する箇所で自然に挿入してください:
{internal_links}
"""

    base_rules = f"""
## 文体ルール
- 冒頭は読者の疑問を代弁する一文から始める（例：「〜と思ったことはありませんか？」）
- 冒頭直後に結論を書く（読者を待たせない）
- 話しかけるような親しみやすい口調
- 短い文でテンポよく（1文40文字以内を目安）
- 具体的な数字や例を入れる（料金は必ず正確に記載）
- 読者が「へぇ」と思う意外な事実を各セクションに1つ入れる（「意外な事実：」で始める）
- 同じフレーズを繰り返さない（「ぶっちゃけ」「実は」は各1回まで）
- 各セクションに具体的な使用シーンや体験談風のエピソードを入れる
- 文末のバリエーションを持たせる（「です」「ます」「でしょう」「ください」「おすすめ」を交互に）

## 比較表・データ
- 比較対象がある場合は必ずマークダウンテーブルで比較表を作る
- 記事内にテーブルを最低2つ入れる
- 最後に「用途別おすすめ早見表」を入れる

## SEOルール
- タイトルにキーワード＋数字＋年号を入れる（例：「5つの視点で比較【2026年版】」）
- h2は4〜6個、h3は各h2の下に2〜3個
- キーワードを自然にh2に含める
- 冒頭100文字以内にキーワードを入れる
- 最後に「まとめ」と具体的な次のアクション

## 収益化リンク（本文中の適切な箇所に自然に挿入すること）
{affiliate_section}

## 収益化ルール
- 紹介するAIツールは実在する有名なものだけ
- 各ツールの料金プランを正確に記載する
- 公式サイトへのリンクを[ツール名](公式URL)形式で入れる
- 「無料プランあり」「◯日間無料トライアル」などの情報を強調
- アフィリエイトリンクは記事内に最低3箇所に分散配置する：
  1. 冒頭の結論部分（「結論から言うと〇〇がおすすめ → [リンク]」）
  2. 本文の該当ツール解説セクション内
  3. 記事末尾の「今すぐ始める3ステップ」セクション
- 各リンクの前後には読者の行動を促す一文を入れる（例：「無料で始められるので、まずは試してみてください」）
- 「期間限定」「今なら」などの緊急性ワードを自然に使う
- 料金比較表には必ず「無料お試し」列を入れる

{internal_links_instruction}

## 禁止
- 嘘の情報・確信のない数字・古い料金情報
- 他サイトのコピペ感
- 「〜です。〜です。」の単調な繰り返し
- 1文が60文字を超える長文
- 「会話形式」と「対話形式」のような意味のない区別
- 内容の薄いセクション（各h2は最低200文字）

## 出力形式
---
title: "タイトル（32文字以内・数字か疑問形＋年号入り）"
description: "メタディスクリプション（80〜120文字・キーワード含む・行動喚起入り）"
---

本文（4000〜5000文字）

※本文の最後には必ず以下のセクションを入れること：
### 今すぐ始める3ステップ
1. [具体的なステップ1]
2. [具体的なステップ2]
3. [具体的なステップ3]

上記ステップ内にアフィリエイトリンクを自然に組み込むこと。
"""

    if article_type == "comparison":
        specific = """
## 記事の構成
1. 結論を最初に書く（「○○な人は△△、□□な人は××がおすすめ」）
2. 比較表（料金・機能・使いやすさ）をマークダウンテーブルで
3. 各ツールの強み・弱みを具体的に
4. 用途別のおすすめを提示
5. おすすめツールまとめ（リンク付き）
"""
    elif article_type == "ranking":
        specific = """
## 記事の構成
1. ランキング結果を冒頭で一覧表示
2. 各ツールを「おすすめ度」「料金」「特徴」で紹介
3. 選ぶ基準を3つ提示
4. 用途別おすすめ
5. おすすめツールまとめ（リンク付き）
"""
    elif article_type == "howto":
        specific = """
## 記事の構成
1. この記事を読むとできるようになることを最初に書く
2. 手順をステップ形式（Step1, Step2...）で
3. よくある失敗と対策
4. 上級者向けのコツを1つ
5. おすすめツールまとめ（リンク付き）
"""
    elif article_type == "problem":
        specific = """
## 記事の構成
1. 読者の悩みに共感する冒頭
2. 原因を簡潔に説明
3. 解決策を3つ提示（具体的に）
4. おすすめの代替ツール（リンク付き）
5. まとめ
"""
    else:  # news
        specific = """
## 記事の構成
1. 最新情報のポイントを3行で
2. 何が変わったのか詳しく
3. ユーザーへの影響
4. 今後の予測
5. 関連ツールまとめ（リンク付き）
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
        "max_tokens": 8000,
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
                tags = [k for k in keyword.split() if len(k) > 1][:5]
                frontmatter += f'tags: {json.dumps(tags, ensure_ascii=False)}\n'
            if "slug:" not in frontmatter:
                frontmatter += f'slug: "{slug}"\n'
            content = f"---{frontmatter}---{body}"
    else:
        tags = [k for k in keyword.split() if len(k) > 1][:5]
        content = f"""---
title: "{keyword}"
description: "{keyword}に関する最新情報をわかりやすく解説"
date: "{today}"
categories: ["AIツール"]
tags: {json.dumps(tags, ensure_ascii=False)}
slug: "{slug}"
---

{content}"""

    filepath.write_text(content, encoding="utf-8")
    print(f"記事を保存: {filepath}")
    return filepath


MIN_ARTICLE_LENGTH = 2500  # 最低文字数（これ以下は再生成）
MAX_RETRIES = 2  # 再生成の最大回数


def validate_article(article):
    """記事の品質チェック"""
    # frontmatterを除いた本文の長さをチェック
    body = article
    if "---" in article:
        parts = article.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]

    body_length = len(body.strip())
    if body_length < MIN_ARTICLE_LENGTH:
        return False, f"本文が短すぎます（{body_length}文字 < {MIN_ARTICLE_LENGTH}文字）"

    # h2見出しが最低3つあるか
    h2_count = body.count("\n## ")
    if h2_count < 3:
        return False, f"h2見出しが少なすぎます（{h2_count}個 < 3個）"

    return True, "OK"


def main():
    print("=== AI Tools Lab 記事生成 v3 ===")
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

    # 3. 記事生成（品質チェック付きリトライ）
    article = None
    for attempt in range(MAX_RETRIES + 1):
        print(f"記事生成中...（試行 {attempt + 1}/{MAX_RETRIES + 1}）")
        article = generate_article_with_ai(keyword, article_type, keyword_info)

        is_valid, reason = validate_article(article)
        if is_valid:
            print(f"品質チェック: OK")
            break
        else:
            print(f"品質チェック: NG — {reason}")
            if attempt < MAX_RETRIES:
                print("再生成します...")
            else:
                print("最大試行回数に達しました。最後の生成結果を使用します。")

    # 4. 保存
    save_article(article, keyword)

    print("=== 完了 ===")


if __name__ == "__main__":
    main()
