#!/usr/bin/env python3
"""
動画の生成とローカルでのテストを行うシンプルなスクリプト
YouTubeアップロードをスキップして機能をテスト
"""
import os
import sys
import logging
import tempfile
from datetime import datetime

# 親ディレクトリをインポートパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
from modules.text_generator import TextGenerator
from modules.video_creator import VideoCreator

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('video-test')

def test_video_creation(theme=None):
    """テスト用に動画を生成し、ローカル保存"""
    try:
        # テキスト生成器初期化
        text_generator = TextGenerator()
        # 動画生成器初期化
        video_creator = VideoCreator()
        
        # テーマが指定されていなければデフォルトを使用
        theme = theme or "テスト"
        
        # 1. テキスト生成
        logger.info(f"「{theme}」についてのテキスト生成開始")
        text, slug = text_generator.generate_text(theme)
        if not text:
            logger.error("テキスト生成に失敗しました")
            return None
        
        logger.info(f"生成されたテキスト:\n{text}")
        
        # 出力ファイル名を作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"{slug}_{timestamp}"
        output_path = os.path.join(config.OUTPUT_DIR, f"{output_name}.mp4")
        
        # 2. 動画作成
        logger.info("動画の生成を開始します")
        video_path = video_creator.create_video(text, output_path, subtitles=text)
        
        if not video_path or not os.path.exists(video_path):
            logger.error("動画作成に失敗しました")
            return None
        
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        logger.info(f"動画が正常に生成されました: {video_path} (サイズ: {file_size_mb:.2f} MB)")
        
        # 動画ファイルのパスを返す
        return video_path
        
    except Exception as e:
        logger.error(f"テスト中にエラーが発生: {str(e)}")
        return None

def play_video(video_path):
    """可能であれば動画を再生"""
    if not os.path.exists(video_path):
        logger.error(f"動画ファイルが見つかりません: {video_path}")
        return False
    
    # プラットフォームに応じたプレイヤーコマンドを試行
    import platform
    import subprocess
    
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["open", video_path])
            return True
        elif system == "Windows":
            os.startfile(video_path)
            return True
        elif system == "Linux":
            players = ["xdg-open", "mpv", "vlc", "mplayer"]
            for player in players:
                try:
                    subprocess.run([player, video_path], check=True)
                    return True
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
            return False
        else:
            logger.warning(f"サポートされていないプラットフォーム: {system}")
            return False
    except Exception as e:
        logger.error(f"動画再生中にエラーが発生: {e}")
        return False

if __name__ == "__main__":
    # コマンドライン引数からテーマを取得
    theme = sys.argv[1] if len(sys.argv) > 1 else "テスト動画"
    
    print(f"テーマ「{theme}」の動画を生成します...")
    video_path = test_video_creation(theme)
    
    if video_path:
        print(f"\n✅ 動画が正常に生成されました: {video_path}")
        print("生成した動画を開きますか？ (y/n)")
        
        if input("> ").lower() in ['y', 'yes']:
            if play_video(video_path):
                print("動画を再生中...")
            else:
                print("動画を再生できませんでした。手動でファイルを開いてください。")
    else:
        print("\n❌ 動画の生成に失敗しました")
        sys.exit(1)
