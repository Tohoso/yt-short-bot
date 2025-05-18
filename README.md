# YouTube ショート自動投稿システム

Discordからのコマンドでテーマを受け取り、AIで文章を生成し、背景動画と合成してYouTubeショート動画を自動投稿するシステムです。

## 機能

- Discordボットによるテーマ入力インターフェース
- AIによる文章自動生成
- 文字と背景動画の合成による動画作成
- YouTubeへの自動アップロード（限定公開）
- シンプルな6秒程度のテキスト表示ショート動画

## セットアップ

1. リポジトリをクローン
```
git clone https://github.com/yourusername/yt-short-bot.git
cd yt-short-bot
```

2. 仮想環境の作成と有効化
```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 必要なパッケージのインストール
```
pip install -r requirements.txt
```

4. 環境変数の設定
`.env.example`ファイルを`.env`にコピーし、必要な情報を入力します。

5. 認証情報の設定
`credentials/`ディレクトリに必要な認証情報ファイルを配置します。
詳細は`credentials/README.md`を参照してください。

6. 背景動画の準備
`assets/backgrounds/`ディレクトリに使用したい背景動画（フリー素材）を配置します。

## 使い方

1. メインスクリプトを実行
```
python main.py
```

2. Discordで指定チャンネルに以下のようにテーマを送信
```
!shorts テーマ名
```

3. システムが自動的に動画を生成し、YouTubeに限定公開でアップロードします

## ライセンス

MIT
