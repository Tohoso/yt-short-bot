"""
YouTubeに動画をアップロードするモジュール
"""
import os
import sys
import logging
import pickle
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# 親ディレクトリをインポートパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger('youtube-shorts-bot.youtube_uploader')

# YouTube APIの設定
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

class YouTubeUploader:
    """YouTubeアップロードクラス"""
    
    def __init__(self, client_secrets_file=None, credentials_dir=None):
        """初期化"""
        self.client_secrets_file = client_secrets_file or config.YOUTUBE_CLIENT_SECRETS_FILE
        self.credentials_dir = credentials_dir or config.CREDENTIALS_DIR
        self.token_pickle_path = os.path.join(self.credentials_dir, 'youtube_token.pickle')
        self.youtube_service = None
    
    def authenticate(self):
        """
        YouTube APIに認証する
        
        Returns:
            bool: 認証成功でTrue、失敗でFalse
        """
        try:
            credentials = None
            
            # トークンがあれば読み込む
            if os.path.exists(self.token_pickle_path):
                logger.info("保存された認証情報を読み込み中...")
                with open(self.token_pickle_path, 'rb') as token:
                    credentials = pickle.load(token)
            
            # 有効な認証情報がなければ新規に取得
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    logger.info("認証情報をリフレッシュ中...")
                    credentials.refresh(google.auth.transport.requests.Request())
                else:
                    logger.info("新規認証情報を取得中...")
                    if not os.path.exists(self.client_secrets_file):
                        logger.error(f"client_secrets.jsonが見つかりません: {self.client_secrets_file}")
                        return False
                    
                    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                        self.client_secrets_file, SCOPES)
                    credentials = flow.run_local_server(port=8080)
                
                # 認証情報を保存
                with open(self.token_pickle_path, 'wb') as token:
                    pickle.dump(credentials, token)
            
            # YouTube API clientを初期化
            self.youtube_service = googleapiclient.discovery.build(
                API_SERVICE_NAME, API_VERSION, credentials=credentials)
            
            logger.info("YouTube API認証成功")
            return True
        
        except Exception as e:
            logger.error(f"YouTube API認証中にエラーが発生: {str(e)}")
            return False
    
    def upload_video(self, video_path, title, description, tags=None, category_id='22', privacy_status='unlisted'):
        """
        YouTube動画をアップロードする
        
        Args:
            video_path (str): アップロードする動画ファイルのパス
            title (str): 動画のタイトル
            description (str): 動画の説明
            tags (list, optional): 動画のタグリスト
            category_id (str, optional): 動画カテゴリID (22=人物とブログ)
            privacy_status (str, optional): プライバシー設定 ('public', 'private', 'unlisted')
            
        Returns:
            str: アップロードした動画のID、失敗した場合はNone
        """
        if not self.youtube_service:
            if not self.authenticate():
                return None
        
        if not os.path.exists(video_path):
            logger.error(f"動画ファイルが見つかりません: {video_path}")
            return None
        
        try:
            tags = tags or []
            
            # YouTubeへのアップロード用メタデータ
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # アップロード用のMediaFileUploadオブジェクト
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True
            )
            
            # アップロードリクエスト
            logger.info(f"YouTubeへのアップロード開始: {title}")
            request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # アップロードの実行
            response = request.execute()
            
            video_id = response.get('id')
            logger.info(f"YouTubeへのアップロード完了: https://youtu.be/{video_id}")
            return video_id
            
        except googleapiclient.errors.HttpError as e:
            logger.error(f"YouTubeアップロード中にHTTPエラー: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"YouTubeアップロード中にエラーが発生: {str(e)}")
            return None


if __name__ == "__main__":
    # テスト用コード
    import sys
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        print("使用方法: python youtube_uploader.py <video_path>")
        sys.exit(1)
    
    if not os.path.exists(video_path):
        print(f"エラー: 動画ファイルが見つかりません: {video_path}")
        sys.exit(1)
    
    uploader = YouTubeUploader()
    video_id = uploader.upload_video(
        video_path=video_path,
        title="テストアップロード",
        description="自動アップロードのテストです",
        tags=["テスト", "自動", "アップロード"],
        privacy_status="unlisted"  # 限定公開
    )
    
    if video_id:
        print(f"動画をアップロードしました: https://youtu.be/{video_id}")
    else:
        print("動画のアップロードに失敗しました")
