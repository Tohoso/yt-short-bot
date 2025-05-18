#!/usr/bin/env python3
"""
YouTube動画アップロード機能のテスト用スクリプト
"""
import os
import sys
import logging
from modules.youtube_uploader import YouTubeUploader

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('youtube_test.log')
    ]
)
logger = logging.getLogger('youtube-test')

def test_youtube_upload(video_path):
    """
    YouTube動画アップロード機能のテスト
    
    Args:
        video_path: アップロードするビデオのパス
    """
    if not os.path.exists(video_path):
        logger.error(f"ビデオファイルが見つかりません: {video_path}")
        return False
    
    # 動画ファイル情報を表示
    file_size = os.path.getsize(video_path) / (1024 * 1024)
    logger.info(f"アップロードするファイル: {video_path} (サイズ: {file_size:.2f} MB)")
    
    # YouTubeアップローダーを初期化
    uploader = YouTubeUploader()
    
    # 標準の認証関数を使用（ポート8080）
    logger.info("YouTube APIの認証を開始...")
    if not uploader.authenticate():
        logger.error("YouTube APIの認証に失敗しました")
        return False
    
    # 動画をアップロード
    title = "テスト動画：字幕付きショート"
    description = """
    テスト用のアップロードです。
    自動生成された字幕付き動画です。
    """
    tags = ["テスト", "字幕", "自動生成", "ショート動画"]
    
    logger.info(f"動画のアップロードを開始: {title}")
    video_id = uploader.upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status="unlisted"  # 限定公開
    )
    
    if video_id:
        logger.info(f"アップロード成功！ビデオID: {video_id}")
        logger.info(f"ビデオURL: https://youtu.be/{video_id}")
        return True
    else:
        logger.error("アップロードに失敗しました")
        return False

if __name__ == "__main__":
    # コマンドライン引数からビデオパスを取得、または最新のビデオを使用
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        # デフォルトではoutputsディレクトリの最新の.mp4ファイルを使用
        outputs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
        mp4_files = [f for f in os.listdir(outputs_dir) if f.endswith('.mp4')]
        if not mp4_files:
            print("エラー: outputsディレクトリに.mp4ファイルがありません")
            sys.exit(1)
        
        # 最新の.mp4ファイルを使用
        latest_file = max(mp4_files, key=lambda f: os.path.getmtime(os.path.join(outputs_dir, f)))
        video_path = os.path.join(outputs_dir, latest_file)
    
    print(f"テスト対象のビデオ: {video_path}")
    if test_youtube_upload(video_path):
        print("テスト成功！")
        sys.exit(0)
    else:
        print("テスト失敗！")
        sys.exit(1)
