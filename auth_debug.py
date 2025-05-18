#!/usr/bin/env python3
"""
OAuth認証のデバッグと修正
"""
import os
import sys
import json
import pickle
import logging
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import googleapiclient.discovery

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('oauth-debug')

# 親ディレクトリをインポートパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

# 必要なスコープ
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def debug_client_secrets(client_secrets_file):
    """クライアントシークレットファイルの内容をデバッグ"""
    try:
        with open(client_secrets_file, 'r') as f:
            config_data = json.load(f)
        
        # 構造を確認
        logger.info(f"クライアントシークレットファイル構造: {list(config_data.keys())}")
        
        # 重要な情報を確認（機密情報は表示しない）
        if 'web' in config_data:
            redirect_uris = config_data['web'].get('redirect_uris', [])
            client_type = 'web'
            logger.info(f"クライアントタイプ: WEB")
            logger.info(f"登録されているリダイレクトURI: {redirect_uris}")
            client_id = config_data['web'].get('client_id', '')
            if client_id:
                logger.info(f"クライアントID: {client_id[:5]}...{client_id[-5:]} (先頭と末尾5文字のみ表示)")
            
            auth_uri = config_data['web'].get('auth_uri')
            token_uri = config_data['web'].get('token_uri')
            logger.info(f"認証URI: {auth_uri}")
            logger.info(f"トークンURI: {token_uri}")
        elif 'installed' in config_data:
            redirect_uris = config_data['installed'].get('redirect_uris', [])
            client_type = 'installed'
            logger.info(f"クライアントタイプ: INSTALLED") 
            logger.info(f"登録されているリダイレクトURI: {redirect_uris}")
            client_id = config_data['installed'].get('client_id', '')
            if client_id:
                logger.info(f"クライアントID: {client_id[:5]}...{client_id[-5:]} (先頭と末尾5文字のみ表示)")
            
            auth_uri = config_data['installed'].get('auth_uri')
            token_uri = config_data['installed'].get('token_uri')
            logger.info(f"認証URI: {auth_uri}")
            logger.info(f"トークンURI: {token_uri}")
        
        return client_type, redirect_uris
    except Exception as e:
        logger.error(f"クライアントシークレットファイルの解析エラー: {e}")
        return None, []

def web_auth_flow(client_secrets_file, token_pickle_path):
    """Webアプリケーション用の認証フロー"""
    credentials = None
    
    # トークンがあれば読み込む
    if os.path.exists(token_pickle_path):
        logger.info("保存された認証情報を読み込み中...")
        with open(token_pickle_path, 'rb') as token:
            credentials = pickle.load(token)
    
    # 有効な認証情報がなければ新規に取得
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            logger.info("認証情報をリフレッシュ中...")
            credentials.refresh(Request())
        else:
            logger.info("Webクライアント用の新規認証情報を取得中...")
            
            # クライアントタイプとリダイレクトURIを確認
            client_type, redirect_uris = debug_client_secrets(client_secrets_file)
            
            try:
                # Webクライアント用のフローを作成
                flow = Flow.from_client_secrets_file(
                    client_secrets_file,
                    scopes=SCOPES,
                    redirect_uri=redirect_uris[0] if redirect_uris else 'http://localhost:8080'
                )
                
                # 認証URLを取得
                auth_url, _ = flow.authorization_url(
                    access_type='offline',
                    include_granted_scopes='true'
                )
                
                print("\n")
                print("=" * 80)
                print("以下のURLをブラウザで開いて認証を行ってください:")
                print(auth_url)
                print("=" * 80)
                print("\n認証後、ブラウザに表示されるコードをここに貼り付けてください:")
                code = input("> ")
                
                # 認証コードを使用してクレデンシャルを取得
                flow.fetch_token(code=code)
                credentials = flow.credentials
                
                # 認証情報を保存
                with open(token_pickle_path, 'wb') as token:
                    pickle.dump(credentials, token)
                    
            except Exception as e:
                logger.error(f"認証フローの実行中にエラー: {e}")
                raise e
    
    return credentials

def main():
    """メイン関数"""
    # クライアントシークレットファイルのパス
    client_secrets_file = config.YOUTUBE_CLIENT_SECRETS_FILE
    # トークン保存先パス（デバッグ用に別ファイルを使用）
    token_pickle_path = os.path.join(config.CREDENTIALS_DIR, 'youtube_token_debug.pickle')
    
    # クライアントシークレットの構造をデバッグ
    logger.info(f"クライアントシークレットファイルのデバッグを開始: {client_secrets_file}")
    client_type, redirect_uris = debug_client_secrets(client_secrets_file)
    
    # クライアントタイプに合わせた認証フロー
    try:
        logger.info("認証フローを開始します...")
        credentials = web_auth_flow(client_secrets_file, token_pickle_path)
        
        # YouTube API clientを初期化
        youtube = googleapiclient.discovery.build(
            'youtube', 'v3', credentials=credentials)
        
        # チャンネル情報を取得（認証テスト）
        logger.info("YouTubeチャンネル情報を取得中...")
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        response = request.execute()
        
        if response.get('items'):
            channel = response['items'][0]
            logger.info(f"認証成功！チャンネル名: {channel['snippet']['title']}")
            logger.info(f"チャンネルID: {channel['id']}")
            logger.info(f"登録者数: {channel.get('statistics', {}).get('subscriberCount', 'N/A')}")
            
            # 認証情報が正常に取得できたのでアップロード可能
            return True
        else:
            logger.error("チャンネル情報の取得に失敗しました")
            return False
        
    except Exception as e:
        logger.error(f"認証テスト中にエラーが発生: {e}")
        return False

if __name__ == "__main__":
    if main():
        print("\n✅ YouTube API認証テスト成功！アップロードが可能になりました。")
    else:
        print("\n❌ YouTube API認証テスト失敗")
        sys.exit(1)
