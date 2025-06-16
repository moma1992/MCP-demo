# Custom MCP Tools Server

FastMCPフレームワークを使用したPython製のMCP（Model Context Protocol）サーバーです。Claude Desktopで使用することで、カスタムツール機能（計算機能とGitHub API連携機能）を提供します。

## 機能

このMCPサーバーは以下の機能を提供します：

- **計算機能**：基本的な数値演算（現在は加算のみ）
- **GitHub連携**：
  - リポジトリ情報の取得
  - イシューの一覧表示・作成
  - プルリクエストの一覧表示

## 必要な環境

- Python 3.11以上
- uv（Pythonパッケージマネージャー）
- Claude Desktop

## 環境構築

### 1. uvのインストール

まず、uvをインストールします（未インストールの場合）：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. プロジェクトのセットアップ

```bash
# リポジトリをクローン
git clone <your-repository-url>
cd mcp-demo

# 依存関係をインストール
uv sync

# 開発用依存関係も含める場合
uv sync --dev
```

### 3. 環境変数の設定（オプション）

GitHub API機能を使用する場合は、GitHubトークンを設定します：

```bash
# .envファイルを作成
echo "GITHUB_TOKEN=your_github_token_here" > .env
```

GitHubトークンの取得方法：
1. GitHub設定 → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)"をクリック
3. 必要な権限を選択（リポジトリ操作にはrepo権限が必要）
4. トークンを生成してコピー

## Claude Desktopでの設定

### 1. Claude Desktop設定ファイルの場所

Claude Desktopの設定ファイルを編集します：

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 2. 設定ファイルの編集

設定ファイルに以下の内容を追加します：

```json
{
  "mcpServers": {
    "custom-tools": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "custom_mcp"
      ],
      "cwd": "/path/to/your/mcp-demo"
    }
  }
}
```

**重要：** `"cwd"`の値を実際のプロジェクトパスに変更してください。

例：
```json
{
  "mcpServers": {
    "custom-tools": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "custom_mcp"
      ],
      "cwd": "/Users/username/mcp-demo"
    }
  }
}
```

### 3. Claude Desktopの再起動

設定を保存した後、Claude Desktopを完全に終了して再起動します。

## 使用方法

Claude Desktopでサーバーが正常に読み込まれると、以下のような操作が可能になります：

### 計算機能
```
「5と3を足して」
```

### GitHub機能
```
「anthropicsのclaude-3-docsリポジトリの情報を教えて」
「microsoft/vscodeのオープンなイシューを一覧表示して」
```

## ローカル開発

### 開発用コマンド

```bash
# コード品質チェック
uv run ruff check          # リンター実行
uv run ruff format         # コードフォーマット
uv run mypy .              # 型チェック

# テスト実行
uv run pytest             # 全テスト実行
uv run pytest --cov       # カバレッジ付きテスト
uv run pytest -v          # 詳細出力

# 開発サーバー起動
uv run python -m custom_mcp  # STDIO版（Claude Desktop用）
```

### 依存関係の管理

```bash
# 新しい依存関係を追加
uv add package_name

# 開発用依存関係を追加
uv add --dev package_name

# 依存関係を削除
uv remove package_name

# lockファイルを更新
uv lock
```

## トラブルシューティング

### Claude Desktopで認識されない場合

1. **パスの確認**：設定ファイルの`cwd`が正しいか確認
2. **uvのパス確認**：`which uv`でuvのパスを確認し、必要に応じてフルパスを使用
3. **権限の確認**：ディレクトリとファイルに適切な読み取り権限があるか確認
4. **ログの確認**：Claude Desktopのログでエラーメッセージを確認

### Python環境の問題

```bash
# Python版の確認
python --version  # 3.11以上である必要があります

# uv環境の確認
uv python list

# 依存関係の再インストール
uv sync --reinstall
```

### デバッグ用の手動実行

```bash
# MCPサーバーを手動で起動してテスト
cd /path/to/mcp-demo
uv run python -m custom_mcp
```

## 開発に参加する

### コード品質の維持

```bash
# pre-commitフックのインストール
uv run pre-commit install

# 全ファイルに対してフックを実行
uv run pre-commit run --all-files
```

### プロジェクト構造

```
mcp-demo/
├── src/custom_mcp/         # メインパッケージ
│   ├── __init__.py
│   ├── __main__.py         # パッケージエントリポイント
│   ├── calculator.py       # MCPツール統合
│   ├── calculator_tools.py # 数学系ツール
│   ├── github_tools.py     # GitHub APIツール
│   └── server.py          # STDIO輸送実装
├── tests/                  # テストスイート
├── pyproject.toml         # プロジェクト設定
└── CLAUDE.md              # Claude Code用指示
```

## ライセンス

MIT License