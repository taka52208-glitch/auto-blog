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

### ステップ4: Groq APIキーを取得
1. https://console.groq.com にアクセス
2. アカウント作成
3. APIキーを発行（無料枠あり）

### ステップ5: GitHubにAPIキーを設定
1. リポジトリの Settings → Secrets and variables → Actions
2. 「New repository secret」をクリック
3. Name: `GROQ_API_KEY`
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

- **毎日朝9時と夕方18時**に自動で計2記事が投稿されます
- 何もしなくてOK
- 1ヶ月で約60記事が貯まります

## 収益化ロードマップ

### Phase 1: 記事蓄積（1〜2ヶ月目）
- 自動投稿で60〜120記事を貯める
- この期間の収益: ほぼ0円

### Phase 2: AdSense申請（記事30本以上で申請可能）
1. Google AdSense に申請: https://www.google.com/adsense
2. 審査通過後、以下3ファイルのAdSenseコメントを外す:
   - `layouts/partials/head-additions.html`（ヘッダー広告コード）
   - `layouts/index.html`（トップページ広告）
   - `layouts/_default/single.html`（記事ページ広告）
3. `ca-pub-あなたのID` と `あなたのスロットID` を実際の値に置換

### Phase 3: アフィリエイト登録（並行して進める）
1. **A8.net** に登録: https://www.a8.net
2. **もしもアフィリエイト** に登録: https://af.moshimo.com
3. AIツール関連の広告主と提携
4. `scripts/generate_article.py` の `AFFILIATE_LINKS` のURLを実際のアフィリエイトリンクに差し替え

### Phase 4: 月1万円達成の目安
| 収益源 | 目標 | 月額 |
|--------|------|------|
| AdSense（月1万PV想定） | RPM 300円 | 約3,000円 |
| アフィリエイト成約 | 月5〜10件 | 約5,000〜10,000円 |
| **合計** | | **約8,000〜13,000円** |

## 費用

| 項目 | 月額 |
|------|------|
| GitHub Pages | 無料 |
| GitHub Actions | 無料（月2000分まで） |
| Groq API（Llama 3.3） | 無料枠あり（超過分は従量課金） |
| **合計** | **ほぼ無料（無料枠内の場合）** |

## SEO機能（自動）

- 構造化データ（JSON-LD）で検索結果のリッチスニペット対応
- OGPタグでSNSシェア時の表示最適化
- 関連記事の自動表示で回遊率アップ
- 記事間の内部リンク自動挿入でSEO評価向上
- カテゴリ・タグによる記事整理

## 注意事項

- 最初の2〜3ヶ月は収益ほぼゼロです（SEOに時間がかかるため）
- 記事の品質を上げたい場合は、スクリプトのプロンプトを調整してください
- AdSense審査にはある程度の記事数と品質が必要です（目安: 30記事以上）
- アフィリエイトリンクは必ず実際のASPリンクに差し替えてください
