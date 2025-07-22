# YouTube Channel Management MCP

個人向けのYouTubeチャンネル管理MCPサーバーです。チャンネルのコンテンツ管理、インサイト分析、企画提案機能を提供します。

## 🚀 主要機能

### 📹 チャンネル管理機能
- **動画一括操作**: チャンネル内の全動画を取得・管理
- **メタデータ更新**: タイトル、説明、タグを一括または個別に更新
- **チャプター追加**: 動画の説明欄に自動で目次を追加
- **バズるタイトル生成**: AIによるタイトル最適化提案

### 📊 分析機能
- **チャンネル分析**: 視聴回数、エンゲージメント率、成長率を分析
- **動画パフォーマンス比較**: 各動画のパフォーマンスを比較分析
- **視聴者インサイト**: 視聴者の属性、視聴時間帯、リテンション率を分析

### 🤖 AI機能
- **企画提案**: トレンド分析に基づく次の動画企画提案
- **成功パターン抽出**: 過去の成功動画から共通パターンを抽出
- **投稿スケジュール最適化**: 最適な投稿時間と頻度を提案

## 🔧 セットアップ

### 1. 依存関係のインストール

```bash
# プロジェクトディレクトリで実行
uv sync
```

### 2. YouTube OAuth認証の設定

#### Google Cloud Consoleでの設定

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成または選択
3. 必要なAPIを有効化:
   - YouTube Data API v3
   - YouTube Analytics API
4. OAuth 2.0認証情報を作成:
   - 「APIとサービス」→「認証情報」
   - 「認証情報を作成」→「OAuth クライアント ID」
   - アプリケーションの種類: 「デスクトップ」
5. JSONファイルをダウンロードし、以下の場所に保存:
   ```
   ~/.youtube_mcp/credentials.json
   ```

#### 環境変数の設定

`.env`ファイルに以下を追加（オプション）:

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 3. 初回認証

MCPツールを初回実行時に、ブラウザが開いてGoogleアカウントでの認証が求められます。

## 📚 利用可能なMCPツール

### チャンネル管理ツール

#### `list_my_videos_tool`
自分のYouTubeチャンネルの動画一覧を取得

```json
{
  "max_results": 50,
  "page_token": null
}
```

#### `update_video_metadata_tool`
動画のメタデータを更新

```json
{
  "video_id": "your_video_id",
  "title": "新しいタイトル",
  "description": "新しい説明",
  "tags": ["tag1", "tag2", "tag3"]
}
```

#### `batch_update_videos_tool`
複数の動画を一括更新

```json
{
  "updates": "[{\"video_id\": \"abc123\", \"title\": \"新タイトル1\"}, {\"video_id\": \"def456\", \"title\": \"新タイトル2\"}]"
}
```

#### `add_video_chapters_tool`
動画にチャプター（目次）を追加

```json
{
  "video_id": "your_video_id",
  "chapters": "[{\"time\": \"0:00\", \"title\": \"イントロ\"}, {\"time\": \"1:30\", \"title\": \"本編\"}]"
}
```

### 分析ツール

#### `get_channel_analytics_tool`
チャンネル全体の分析データを取得

```json
{
  "days": 30
}
```

#### `get_video_analytics_tool`
特定の動画の詳細分析

```json
{
  "video_id": "your_video_id",
  "days": 30
}
```

#### `analyze_audience_insights_tool`
視聴者インサイトを分析

```json
{
  "days": 30
}
```

#### `compare_video_performance_tool`
複数動画のパフォーマンス比較

```json
{
  "video_ids": "video1,video2,video3",
  "days": 30
}
```

### AI機能ツール

#### `generate_optimized_titles_tool`
AIベースの最適化されたタイトルを生成

```json
{
  "video_id": "your_video_id",
  "target_audience": "若年層"
}
```

利用可能なターゲット層: `若年層`, `ビジネス`, `主婦層`, `シニア`

#### `suggest_next_content_tool`
次の動画企画を提案

```json
{
  "category": "ゲーム"
}
```

利用可能なカテゴリ: `ゲーム`, `教育`, `エンタメ`

#### `analyze_success_patterns_tool`
チャンネルの成功パターンを分析

```json
{}
```

#### `optimize_posting_schedule_tool`
最適な投稿スケジュールを提案

```json
{}
```

### セットアップツール

#### `setup_youtube_oauth_tool`
OAuth認証の設定方法を表示

```json
{}
```

## 🎯 使用例

### 1. チャンネルの動画一覧を取得

```json
{
  "tool": "list_my_videos_tool",
  "arguments": {
    "max_results": 20
  }
}
```

### 2. 動画タイトルを一括で「バズる」タイトルに変更

1. まず動画一覧を取得
2. 各動画に対してタイトル提案を生成
3. 一括更新で適用

```json
{
  "tool": "generate_optimized_titles_tool",
  "arguments": {
    "video_id": "abc123",
    "target_audience": "若年層"
  }
}
```

### 3. チャンネルの成功パターンを分析して次の企画を決定

```json
{
  "tool": "analyze_success_patterns_tool",
  "arguments": {}
}
```

```json
{
  "tool": "suggest_next_content_tool",
  "arguments": {
    "category": "エンタメ"
  }
}
```

### 4. 動画にチャプターを追加

```json
{
  "tool": "add_video_chapters_tool",
  "arguments": {
    "video_id": "your_video_id",
    "chapters": "[{\"time\": \"0:00\", \"title\": \"オープニング\"}, {\"time\": \"2:30\", \"title\": \"本題に入る\"}, {\"time\": \"8:15\", \"title\": \"まとめ\"}]"
  }
}
```

## ⚠️ 注意事項

### API制限について

- **YouTube Data API v3**: 1日あたり10,000単位のクォータ制限
- **YouTube Analytics API**: 1日あたり200,000リクエスト制限
- 大量の操作を行う場合は、制限を考慮して実行してください

### セキュリティ

- OAuth認証トークンは `~/.youtube_mcp/token.pickle` に保存されます
- 認証情報は適切に管理し、共有しないでください
- 必要に応じて `revoke_token()` で認証を取り消すことができます

### サポートされている操作

**✅ 可能な操作:**
- 動画のタイトル、説明、タグの更新
- チャンネルと動画の分析データ取得
- 視聴者インサイトの分析

**❌ 制限される操作:**
- チャンネルの基本情報（チャンネル名、説明）の変更（YouTube APIの制限）
- 動画のサムネイル変更（別途YouTube Studioが必要）
- 収益化設定の変更

## 🔧 トラブルシューティング

### 認証エラーが発生した場合

1. `~/.youtube_mcp/credentials.json` が正しく配置されているか確認
2. Google Cloud ConsoleでAPIが有効化されているか確認
3. OAuth認証情報が正しく設定されているか確認

### APIクォータ制限に達した場合

1. 翌日まで待機するか、Google Cloud Consoleでクォータ増加を申請
2. 一度に処理する動画数を減らす
3. バッチ操作を小分けして実行

### 動画が見つからないエラー

1. 動画IDが正しいか確認
2. 動画がプライベートまたは削除されていないか確認
3. チャンネルの所有者であることを確認

## 📈 今後の拡張予定

- **自動投稿機能**: スケジュールに基づく自動投稿
- **競合分析**: 同じカテゴリの他チャンネルとの比較
- **A/Bテスト**: タイトルやサムネイルのA/Bテスト機能
- **レポート生成**: 定期的なパフォーマンスレポート作成
- **通知機能**: 目標達成時の自動通知

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. エラーメッセージの詳細
2. 実行したコマンドと引数
3. YouTube API Console のログ
4. 認証状態の確認

---

このMCPサーバーにより、YouTubeチャンネル運営を効率化し、データに基づいた戦略的な意思決定を支援します。