# 自動ブログ セットアップ手順

## あなたがやること（1回だけ、約30分）

### ステップ1: GitHubアカウント作成
1. https://github.com にアクセス
2. アカウントを作成（無料）

### ステップ2: リポジトリを作成
1. GitHub で「New Repository」をクリック
2. リポジトリ名: `auto-blog`
3. Public を選択
4. 「Create repository」をクリック

### ステップ3: このコードをアップロード
```bash
cd auto-blog
git init
git add -A
git commit -m "初回セットアップ"
git remote add origin https://github.com/あなたのユーザー名/auto-blog.git
git push -u origin main
```

### ステップ4: Anthropic APIキーを取得
1. https://console.anthropic.com にアクセス
2. アカウント作成
3. APIキーを発行（最初$5分の無料クレジットあり）

### ステップ5: GitHubにAPIキーを設定
1. リポジトリの Settings → Secrets and variables → Actions
2. 「New repository secret」をクリック
3. Name: `ANTHROPIC_API_KEY`
4. Value: 取得したAPIキー
5. 「Add secret」をクリック

### ステップ6: GitHub Pages を有効化
1. リポジトリの Settings → Pages
2. Source: 「GitHub Actions」を選択

### ステップ7: Hugo テーマをインストール
```bash
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke
git commit -m "テーマ追加"
git push
```

### ステップ8: 動作確認
1. リポジトリの Actions タブへ
2. 「毎日自動記事投稿」を選択
3. 「Run workflow」をクリック（手動テスト）
4. 成功したら、毎日自動で記事が投稿されます

---

## セットアップ後

- **毎日朝9時**に自動で1記事が投稿されます
- 何もしなくてOK
- 1ヶ月で約30記事が貯まります

## 収益化（記事が30本以上貯まったら）

1. Google AdSense に申請
   - https://www.google.com/adsense
   - サイトURLを登録
   - 審査通過後、広告が自動表示される

2. 審査通過したら `layouts/index.html` のAdSenseコメントを外す

## 費用

| 項目 | 月額 |
|------|------|
| GitHub Pages | 無料 |
| GitHub Actions | 無料（月2000分まで） |
| Anthropic API（Haiku） | 約¥500〜¥1,500 |
| **合計** | **約¥500〜¥1,500/月** |

## 注意事項

- 最初の3〜6ヶ月は収益ほぼゼロです（SEOに時間がかかるため）
- 記事の品質を上げたい場合は、スクリプトのプロンプトを調整してください
- AdSense審査にはある程度の記事数と品質が必要です（目安: 30記事以上）
