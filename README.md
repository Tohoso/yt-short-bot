# YouTube ショート自動投稿システム

Discordからのコマンドでテーマを受け取り、AIで文章を生成し、背景動画と合成してYouTubeショート動画を自動投稿するシステムです。

## 機能

- Discordボットによるテーマ入力インターフェース
- AIによる文章自動生成
- FFmpegによる高品質な動画処理
- 完全にカスタマイズ可能な字幕表示機能
- 背景動画の自動クロップとトリミング
- YouTubeへの自動アップロード（限定公開）
- シンプルな6秒程度のテキスト表示ショート動画

## セットアップ

1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/yt-short-bot.git
cd yt-short-bot
```

2. 仮想環境の作成と有効化

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

4. FFmpegのインストール

システムに合わせてFFmpegをインストールします。

macOS:

```bash
brew install ffmpeg
```

Ubuntu/Debian:

```bash
apt-get install ffmpeg
```

Windows:
[FFmpeg公式Website](https://ffmpeg.org/download.html)からダウンロードし、PATHに追加。

5. 環境変数の設定

`.env.example`ファイルを`.env`にコピーし、必要な情報を入力します。

6. 認証情報の設定

`credentials/`ディレクトリに必要な認証情報ファイルを配置します。
詳細は`credentials/README.md`を参照してください。

7. 背景動画の準備

`assets/backgrounds/`ディレクトリに使用したい背景動画（フリー素材）を配置します。

## 使い方

1. メインスクリプトを実行

```bash
python main.py
```

2. Discordで指定チャンネルに以下のようにテーマを送信

```bash
!shorts テーマ名
```

3. システムが以下の処理を自動的に行います
   - AIによる文章生成
   - 字幕付き動画の作成
   - YouTubeに限定公開でアップロード
   - Discord上での結果通知

## コード構成

- `main.py` - メインアプリケーションエントリポイント
- `config.py` - 設定ファイル

### modules/

- `text_generator.py` - AIを使ってテキストを生成
- `video_creator.py` - 動画生成の中心処理
- `ffmpeg_handler.py` - FFmpegコマンド処理
- `subtitle_utils.py` - 字幕生成ユーティリティ
- `youtube_uploader.py` - YouTube APIを使って動画アップロード
- `discord_bot.py` - Discordとの連携処理

## 字幕表示機能

生成されたテキストは、FFmpegのdrawtextフィルターを使用して動画に直接描画されます。以下のパラメータがカスタマイズ可能です：

- フォントサイズ
- テキストの色
- 背景ボックスの不透明度
- テキストの配置と間隔

## ライセンス

MIT
