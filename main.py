"""
YouTubeショート自動生成・投稿システムのメインエントリーポイント
"""
import os
import sys
import logging
import asyncio
from datetime import datetime

# 自作モジュールのインポート
import config
from modules.text_generator import TextGenerator
from modules.video_creator import VideoCreator
from modules.youtube_uploader import YouTubeUploader
from modules.discord_bot import DiscordBot

logger = logging.getLogger('youtube-shorts-bot.main')

class YouTubeShortsBot:
    """YouTubeショート自動生成・投稿システムのメインクラス"""
    
    def __init__(self):
        """初期化"""
        # 設定の検証
        if not config.validate_config():
            logger.error("設定の検証に失敗しました。終了します。")
            sys.exit(1)
        
        # ディレクトリの確認
        config.ensure_directories()
        
        # モジュールの初期化
        self.text_generator = TextGenerator()
        self.video_creator = VideoCreator()
        self.youtube_uploader = YouTubeUploader()
        self.discord_bot = DiscordBot()
        
        # Discordボットのコールバック設定
        self.discord_bot.set_callback(self.process_shorts_request)
    
    async def process_shorts_request(self, theme):
        """
        ショート動画リクエストを処理する
        
        Args:
            theme (str): 動画のテーマ
            
        Returns:
            dict: 処理結果
        """
        try:
            logger.info(f"「{theme}」のショート動画生成開始")
            
            # 1. テキスト生成
            text, slug = self.text_generator.generate_text(theme)
            if not text:
                return {'success': False, 'error': 'テキスト生成に失敗しました'}
            
            # 出力ファイル名を作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{slug}_{timestamp}"
            
            # 2. 動画作成
            video_path = self.video_creator.create_video(text, output_name)
            if not video_path:
                return {'success': False, 'error': '動画作成に失敗しました'}
            
            # 3. YouTube認証
            if not self.youtube_uploader.authenticate():
                return {'success': False, 'error': 'YouTube認証に失敗しました'}
            
            # 4. YouTubeアップロード
            title = f"{theme} | ショート動画"
            description = f"{theme}についてのショート動画です。\n\n{text}"
            tags = [theme, "ショート", "shorts", "自動生成"]
            
            video_id = self.youtube_uploader.upload_video(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                privacy_status="unlisted"  # 限定公開
            )
            
            if not video_id:
                return {'success': False, 'error': 'YouTubeアップロードに失敗しました'}
            
            # 成功レスポンス
            return {
                'success': True,
                'video_id': video_id,
                'text': text,
                'video_path': video_path
            }
            
        except Exception as e:
            logger.error(f"処理中にエラーが発生: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def run(self):
        """ボットを起動"""
        logger.info("YouTube Shorts自動生成・投稿システムを起動中...")
        
        # Discordボット起動（ブロッキング呼び出し）
        self.discord_bot.run()


if __name__ == "__main__":
    # ロギング設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log')
        ]
    )
    
    # 単体テスト関数
    async def test_single_theme():
        """テーマを指定して単体テストを実行"""
        # テストするテーマ
        test_theme = "猫"
        
        bot = YouTubeShortsBot()
        result = await bot.process_shorts_request(test_theme)
        
        if result['success']:
            logger.info(f"テスト成功: {result}")
            logger.info(f"動画URL: https://youtu.be/{result['video_id']}")
        else:
            logger.error(f"テスト失敗: {result}")
    
    # 引数によってテストか実行かを切り替え
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # テストモード
        asyncio.run(test_single_theme())
    else:
        # 通常実行モード
        bot = YouTubeShortsBot()
        bot.run()
