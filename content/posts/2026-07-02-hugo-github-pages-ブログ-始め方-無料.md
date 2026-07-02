---
title: "Hugo＋GitHub Pagesでブログを無料で始める手順｜実際に構築した記録"
description: "Hugo（静的サイトジェネレーター）とGitHub Pagesを使って、サーバー代ゼロでブログを立ち上げる手順を解説。実際にこのブログを構築した経験をもとに、つまずきやすいポイントも含めて書きます。"
date: "2026-07-02"
categories: ["AIツール"]
tags: ["Hugo", "GitHub Pages", "ブログ", "無料", "始め方"]
slug: "hugo-github-pages-ブログ-始め方-無料"
---

このブログ（ai-navi-tools.net）は、Hugo + GitHub Pagesで運用しています。月額のサーバー代はゼロ。かかっているのは独自ドメインの年間維持費だけです。

この記事では、Hugoでブログを立ち上げてGitHub Pagesで公開するまでの手順を、実際の構築経験をもとに書きます。

## HugoとGitHub Pagesを選んだ理由

WordPressではなくHugoを選んだ理由は3つあります。

1. **表示が速い。** HugoはHTMLを事前に生成する静的サイトジェネレーターです。サーバーでPHPを動かすWordPressと違い、表示速度が圧倒的に速い。Google PageSpeed Insightsのスコアも高く出ます
2. **サーバー代がかからない。** GitHub Pagesは静的サイトを無料でホスティングできます。WordPressだとレンタルサーバー代が月額1,000円前後かかります
3. **Git管理できる。** 記事も設定もすべてGitで管理できるため、変更履歴が残り、壊しても戻せます

逆にデメリットもあります。コマンドライン操作が必要で、管理画面はありません。プラグインの選択肢もWordPressより少ないです。「記事だけ書きたい」人にはWordPress + [Xserver](https://px.a8.net/svt/ejp?a8mat=4B1RXW+6JSFM+CO4+3H2QRM)のほうが合います。

## Step 1：Hugoをインストールする

### macOSの場合

```
brew install hugo
```

### Ubuntu / WSLの場合

```
sudo apt update
sudo apt install hugo
```

インストール後、バージョンを確認します。

```
hugo version
```

v0.120以降が入っていれば問題ありません。古いバージョンだとテーマが動かないことがあるので、その場合は[Hugo公式のリリースページ](https://github.com/gohugoio/hugo/releases)から最新版をダウンロードしてください。

**ハマったポイント：** Ubuntuのaptで入るHugoはバージョンが古いことがあります。筆者の環境ではaptで入ったのがv0.92で、テーマが正常に動きませんでした。公式から最新版をダウンロードして解決しました。

## Step 2：サイトを作成する

```
hugo new site my-blog
cd my-blog
git init
```

これでサイトの骨格ができます。中身はこうなっています。

```
my-blog/
├── archetypes/    # 記事テンプレート
├── content/       # 記事を置く場所
├── layouts/       # HTMLテンプレート
├── static/        # 画像・CSS等の静的ファイル
├── themes/        # テーマ
└── hugo.toml      # 設定ファイル
```

## Step 3：テーマを追加する

Hugoは単体ではデザインがありません。テーマを追加します。このブログではAnankeテーマを使っています。

```
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke
```

`hugo.toml`にテーマを指定します。

```toml
baseURL = "https://あなたのドメイン/"
languageCode = "ja"
title = "ブログタイトル"
theme = "ananke"
```

この時点でローカルプレビューができます。

```
hugo server -D
```

ブラウザで `http://localhost:1313` を開くと、空のブログが表示されます。

## Step 4：最初の記事を書く

```
hugo new posts/first-post.md
```

`content/posts/first-post.md`が生成されます。中身を編集します。

```markdown
---
title: "最初の記事"
date: 2026-07-02
draft: false
---

ここに本文を書きます。マークダウン記法が使えます。
```

`draft: false`にしないと公開されません。`hugo server -D`なら下書きも表示されますが、本番ビルドでは`draft: true`の記事は除外されます。

## Step 5：GitHubリポジトリを作成してpushする

GitHubで新しいリポジトリを作成します（publicで作成）。

```
git remote add origin https://github.com/あなたのユーザー名/my-blog.git
git add -A
git commit -m "初期構築"
git push -u origin main
```

## Step 6：GitHub Actionsでビルド＆デプロイを自動化する

mainブランチにpushするたびに、Hugoビルド→GitHub Pagesにデプロイするワークフローを作ります。

`.github/workflows/deploy.yml`を作成します。

```yaml
name: Deploy Hugo site

on:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true

      - uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          extended: true

      - run: hugo --minify

      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

このファイルをコミット＆pushすると、GitHub Actionsが動いてgh-pagesブランチにビルド成果物がデプロイされます。

GitHub Pagesの設定で、SourceをBranch: gh-pagesに変更すれば公開完了です。

**ハマったポイント：** `submodules: true`をcheckoutに付け忘れると、テーマが読み込まれずビルドが失敗します。筆者は最初これでエラーになりました。

## Step 7：独自ドメインを設定する（任意）

GitHub Pagesはデフォルトで`ユーザー名.github.io/リポジトリ名`というURLになります。独自ドメインを使いたい場合は以下の手順です。

1. ドメインを取得する（お名前.comやCloudflareなど）
2. DNSにCNAMEレコードを追加（`ユーザー名.github.io`を指す）
3. リポジトリのSettings → Pages → Custom domainにドメインを入力
4. `static/CNAME`ファイルにドメイン名を書く

```
echo "あなたのドメイン.com" > static/CNAME
```

HTTPSは自動で有効になります（反映まで数時間かかることがあります）。

## 構築にかかった時間

このブログを構築したときの実績です。

| 作業 | 所要時間 |
|------|----------|
| Hugoインストール・初期設定 | 30分 |
| テーマ選定・設定 | 1時間 |
| GitHub Actionsの設定 | 1時間 |
| 独自ドメイン設定 | 30分 |
| 最初の記事を書いて公開 | 1時間 |
| **合計** | **約4時間** |

ただしこれはAIコーディングツール（Claude Code）を使った場合です。設定ファイルの生成やエラーの解決をAIに任せたので、手動だともう少しかかると思います。

## Hugo + GitHub Pagesが向いている人・向いていない人

**向いている人：**
- ターミナル操作に抵抗がない
- サーバー代をかけたくない
- 表示速度を重視する
- Gitで管理したい

**向いていない人：**
- 管理画面がないと困る → WordPress + [Xserver](https://px.a8.net/svt/ejp?a8mat=4B1RXW+6JSFM+CO4+3H2QRM)がおすすめ
- プラグインで機能を足したい → Hugoはプラグイン文化が薄い
- 記事を書くことだけに集中したい → noteやはてなブログが手軽

## まとめ

Hugo + GitHub Pagesの組み合わせは、**コストゼロで速いブログ**を作りたい人に最適です。初期設定に多少の技術力が要りますが、一度セットアップすれば記事を書いてpushするだけで更新されます。

このブログ自体がHugo + GitHub Pagesで動いている実例です。構築の詳しい体験記は[Claude Codeでブログを作った全記録](/posts/claude-code-ブログ構築-体験記/)で書いています。

AIを活用したブログの始め方全般は[AIを活用したブログの始め方](/posts/aiブログ-始め方-wordpress-サーバー-おすすめ/)、収益化については[AIブログ収益化のロードマップ](/posts/aiブログ-収益化-月5万-ロードマップ/)をご覧ください。
