# 認証情報の設定方法

このディレクトリには、各種APIとの連携に必要な認証情報を保存します。
セキュリティ上の理由からこれらのファイルはGitリポジトリにはコミットされません。

## 必要な認証情報ファイル

### Discord Bot

1. [Discord Developer Portal](https://discord.com/developers/applications)で新しいアプリケーションを作成
2. Botセクションでボットを追加し、トークンをコピー
3. `discord_token.txt`ファイルを作成し、トークンを保存

### Anthropic API (Claude 3 Sonnet)

1. [Anthropic API Console](https://console.anthropic.com/)でアカウントを作成
2. API Keysセクションで新しいAPIキーを生成
3. `anthropic_api_key.txt`ファイルを作成し、APIキーを保存
4. 使用するモデルは `claude-3-sonnet-20240229` です

### OpenAI API (レガシー対応用)

1. [OpenAI API Keys](https://platform.openai.com/api-keys)からAPIキーを取得
2. `openai_api_key.txt`ファイルを作成し、APIキーを保存

### YouTube API

1. [Google Cloud Console](https://console.cloud.google.com/)で新しいプロジェクトを作成
2. YouTube Data API v3を有効化
3. OAuthクライアントIDを作成（認証情報 > 認証情報を作成 > OAuthクライアントID）
   - アプリケーションの種類: Webアプリケーション
   - リダイレクトURI: `http://localhost:8080`
4. 取得したclient_secrets.jsonファイルをこのディレクトリに保存

## ファイル構成

```
credentials/
├─ discord_token.txt       # Discordボットトークン
├─ anthropic_api_key.txt    # Anthropic APIキー (Claude 3 Sonnet)
├─ openai_api_key.txt      # OpenAI APIキー (レガシー)
└─ client_secrets.json     # YouTube API認証情報
```

**重要**: これらの認証情報は厳重に管理し、公開リポジトリにコミットしないでください。
