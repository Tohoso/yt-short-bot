#!/usr/bin/env python3
"""
OAuthのオフラインモードを使用してYouTube認証テストを行う
"""
import os
import sys
import json
import pickle
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import googleapiclient.discovery

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('youtube-oauth-test')

# 親ディレクトリをインポートパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

# 必要なスコープ
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_credentials(client_secrets_file, token_pickle_path):
    """
    OAuth2認証情報を取得する
    オフラインモードで認証コードを手動入力
    """
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
            logger.info("新規認証情報を取得中（オフラインモード）...")
            
            # クライアントシークレットファイルの内容を出力
            try:
                with open(client_secrets_file, 'r') as f:
                    config_data = json.load(f)
                
                # センシティブ情報は表示しない
                if 'web' in config_data:
                    redirect_uris = config_data['web'].get('redirect_uris', [])
                    client_type = 'web'
                    logger.info(f"クライアントタイプ: WEB")
                elif 'installed' in config_data:
                    redirect_uris = config_data['installed'].get('redirect_uris', [])
                    client_type = 'installed'
                    logger.info(f"クライアントタイプ: INSTALLED") 
                
                logger.info(f"登録されているリダイレクトURI: {redirect_uris}")
            except Exception as e:
                logger.error(f"クライアントシークレットファイルの読み込みエラー: {e}")
            
            # オフラインモードでフローを作成
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES)
            
            # コンソールで認証を実行
            try:
                flow.run_console()
                credentials = flow.credentials
            except Exception as e:
                logger.error(f"認証フローの実行中にエラー: {e}")
                raise e
        
        # 認証情報を保存
        with open(token_pickle_path, 'wb') as token:
            pickle.dump(credentials, token)
    
    return credentials

def main():
    """メイン関数"""
    client_secrets_file = config.YOUTUBE_CLIENT_SECRETS_FILE
    token_pickle_path = os.path.join(config.CREDENTIALS_DIR, 'youtube_token_offline.pickle')
    
    # 認証情報を取得
    try:
        logger.info(f"YouTube API 認証テスト（オフラインモード）を開始...")
        logger.info(f"Client secrets file: {client_secrets_file}")
        credentials = get_credentials(client_secrets_file, token_pickle_path)
        
        # YouTube API clientを作成
        youtube = googleapiclient.discovery.build(
            'youtube', 'v3', credentials=credentials)
        
        # チャンネル情報を取得してテスト
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        response = request.execute()
        
        if response.get('items'):
            channel = response['items'][0]
            logger.info(f"認証成功！チャンネル名: {channel['snippet']['title']}")
            logger.info(f"登録者数: {channel.get('statistics', {}).get('subscriberCount', 'N/A')}")
            logger.info(f"総視聴回数: {channel.get('statistics', {}).get('viewCount', 'N/A')}")
            return True
        else:
            logger.error("チャンネル情報の取得に失敗しました")
            return False
            
    except Exception as e:
        logger.error(f"認証テスト中にエラーが発生: {e}")
        return False

if __name__ == "__main__":
    if main():
        print("YouTube API認証テスト成功！")
    else:
        print("YouTube API認証テスト失敗")
        sys.exit(1)
