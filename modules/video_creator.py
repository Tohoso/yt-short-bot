"""
テキストと背景動画を組み合わせてショート動画を作成するモジュール
"""
import os
import sys
import random
import logging
import math
from datetime import datetime
import glob
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tempfile

# 親ディレクトリをインポートパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 字幕およびFFmpeg関連のモジュールをインポート
from modules.subtitle_utils import write_srt_file
from modules.ffmpeg_handler import crop_video, trim_video, mute_video, add_subtitles_to_video, add_text_to_video

logger = logging.getLogger('youtube-shorts-bot.video_creator')

class VideoCreator:
    """動画作成クラス"""
    
    def __init__(self, output_dir=None, temp_dir=None, backgrounds_dir=None):
        """初期化"""
        self.output_dir = output_dir or config.OUTPUT_DIR
        self.temp_dir = temp_dir or config.TEMP_DIR
        self.backgrounds_dir = backgrounds_dir or config.BACKGROUNDS_DIR
        
        # ディレクトリの存在確認
        for directory in [self.output_dir, self.temp_dir, self.backgrounds_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"ディレクトリを作成しました: {directory}")
    
    def get_random_background(self):
        """
        ランダムな背景動画を選択する
        
        Returns:
            str: 背景動画のパス、見つからない場合はNone
        """
        # 明示的に新しいサンプル動画を使用
        sample_path = os.path.join(self.backgrounds_dir, 'sample_background2.mp4')
        if os.path.exists(sample_path):
            logger.info(f"背景動画を選択: sample_background2.mp4")
            return sample_path
        
        # 以下は元のコード（フォールバック用）
        video_extensions = ['*.mp4', '*.mov', '*.avi', '*.mkv']
        background_files = []
        
        for ext in video_extensions:
            pattern = os.path.join(self.backgrounds_dir, ext)
            background_files.extend(glob.glob(pattern))
        
        if not background_files:
            logger.error(f"背景動画が見つかりません: {self.backgrounds_dir}")
            return None
        
        # ランダムに1つ選択
        random_background = random.choice(background_files)
        logger.info(f"背景動画を選択: {os.path.basename(random_background)}")
        return random_background
    
    def create_text_clip(self, text, duration=None, position='center'):
        """
        テキストクリップを作成する
        
        Args:
            text (str): 表示するテキスト
            duration (float, optional): クリップの長さ（秒）
            position (str or tuple, optional): テキストの位置
            
        Returns:
            TextClip: 作成されたテキストクリップ
        """
        duration = duration or config.VIDEO_DURATION
        
        # 長いテキストは複数行に分割
        if len(text) > 20:
            parts = text.split()
            midpoint = len(parts) // 2
            first_half = ' '.join(parts[:midpoint])
            second_half = ' '.join(parts[midpoint:])
            text = f"{first_half}\n{second_half}"
        
        # テキストクリップ作成
        text_clip = TextClip(
            text,
            fontsize=config.TEXT_SIZE,
            color=config.TEXT_COLOR,
            font=config.TEXT_FONT,
            stroke_color=config.TEXT_STROKE_COLOR,
            stroke_width=config.TEXT_STROKE_WIDTH,
            method='caption',
            align='center',
            size=(config.VIDEO_WIDTH * 0.9, None)  # 幅を少し小さくして余白を持たせる
        )
        
        # 動画の長さに合わせる
        text_clip = text_clip.set_duration(duration)
        
        # 指定の位置に配置
        text_clip = text_clip.set_position(position)
        
        return text_clip

    def create_subtitle_srt(self, subtitle_text, output_path, video_duration=None):
        """
        字幕テキストからSRTファイルを作成する
        
        Args:
            subtitle_text (str): 字幕に表示するテキスト
            output_path (str): 出力するSRTファイルのパス
            video_duration (float, optional): 動画の長さ(秒)
            
        Returns:
            str: 作成されたSRTファイルのパス、失敗した場合はNone
        """
        if not subtitle_text:
            return None
            
        if video_duration is None:
            video_duration = config.VIDEO_DURATION
        
        try:
            # 字幕として表示するテキストをログに記録
            logger.info(f"SRT字幕ファイルを作成: {subtitle_text}")
            
            # SRTファイルを作成
            srt_path = write_srt_file(subtitle_text, output_path, video_duration)
            
            logger.info(f"SRT字幕ファイルを作成しました: {srt_path}")
            return srt_path
            
        except Exception as e:
            logger.error(f"SRT字幕ファイル作成エラー: {e}")
            return None
        
    def create_simple_text_image(self, text, size=(640, 140), bg_color=(0, 0, 0), text_color=(255, 255, 255)):
        """
        テキストを移植した単純な画像を作成する（テスト用）
        
        Args:
            text (str): 表示するテキスト
            size (tuple): 画像サイズ (width, height)
            bg_color (tuple): 背景色 (R, G, B)
            text_color (tuple): テキスト色 (R, G, B)
            
        Returns:
            PIL.Image: 作成された画像
        """
        # 画像の作成
        image = Image.new('RGB', size, color=bg_color)
        draw = ImageDraw.Draw(image)
        
        # テキストの描画（フォントがない場合はデフォルトを使用）
        try:
            # システムフォントを指定してみる（Macの場合）
            font = ImageFont.truetype("Arial", 40)
        except IOError:
            # デフォルトフォントを使用
            font = ImageFont.load_default()
        
        # テキストを中央に配置するための計算
        text_width, text_height = draw.textsize(text, font=font)
        position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
        
        # テキスト描画
        draw.text(position, text, fill=text_color, font=font)
        
        return image
    
    def create_video(self, text=None, output_path=None, background_video_path=None, skip_text=False, subtitles=None, mute_audio=False):
        """
        動画を生成する
        
        Args:
            text (str, optional): 動画に表示するテキスト
            output_path (str, optional): 出力ファイルパス
            background_video_path (str, optional): 背景動画のパス
            skip_text (bool, optional): メインテキストの表示をスキップするか
            subtitles (list or str, optional): 字幕のリストまたはテキスト
            mute_audio (bool, optional): 音声をミュートするか
            
        Returns:
            str: 生成した動画のパス
        """
        try:
            # 出力パスの設定
            if output_path is None:
                output_path = os.path.join(config.OUTPUT_DIR, "output.mp4")
                
            # 出力ディレクトリの確認
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 背景動画選択
            if background_video_path is None:
                background_video_path = self.get_random_background()
                
            if not background_video_path or not os.path.exists(background_video_path):
                raise ValueError(f"背景動画が見つかりません: {background_video_path}")
                
            logger.info(f"背景動画を選択: {os.path.basename(background_video_path)}")
            
            # 一時ファイルを保存するディレクトリ
            temp_dir = tempfile.mkdtemp(prefix="yt_shorts_")
            
            # 処理の流れ：
            # 1. 必要に応じて音声をミュート
            # 2. 動画をクロップして縦長に
            # 3. 動画の長さを調整
            # 4. 字幕を追加
            
            # ステップ1: 中間ファイルのパスを設定
            temp_muted = os.path.join(temp_dir, "muted.mp4") if mute_audio else background_video_path
            temp_cropped = os.path.join(temp_dir, "cropped.mp4")
            temp_trimmed = os.path.join(temp_dir, "trimmed.mp4")
            
            # ステップ2: 必要に応じて音声をミュート
            if mute_audio:
                logger.info("動画の音声を無効化します")
                if not mute_video(background_video_path, temp_muted):
                    raise RuntimeError("音声のミュートに失敗しました")
            
            # ステップ3: 動画を縦長形式に変換
            logger.info("動画を縦長形式に変換します (9:16比率)")
            if not crop_video(temp_muted, temp_cropped, config.VIDEO_WIDTH, config.VIDEO_HEIGHT):
                raise RuntimeError("動画のクロップに失敗しました")
            
            # ステップ4: 動画の長さを調整
            logger.info(f"動画の長さを{config.VIDEO_DURATION}秒に調整します")
            if not trim_video(temp_cropped, temp_trimmed, 0, config.VIDEO_DURATION):
                raise RuntimeError("動画の長さ調整に失敗しました")
            
            # 字幕が指定されている場合
            if subtitles:
                logger.info("字幕を追加します")
                
                # 複数の字幕がある場合は結合して一つの文字列にする
                if isinstance(subtitles, list):
                    subtitle_text = "\n".join([sub['text'] for sub in subtitles])
                else:
                    subtitle_text = subtitles
                
                # 字幕を直接描画
                logger.info(f"FFmpegを使用して字幕を直接描画します: {subtitle_text}")
                if not add_text_to_video(temp_trimmed, output_path, subtitle_text, 
                                      font_size=60, font_color="white", bg_opacity=0.7):
                    raise RuntimeError("字幕の追加に失敗しました")
            else:
                # 字幕なしの場合は、トリミング済みファイルをそのまま出力
                import shutil
                shutil.copy(temp_trimmed, output_path)
            
            # 一時ファイルのクリーンアップ
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"一時ファイルの削除中にエラーが発生: {e}")
            
            logger.info(f"動画の作成が完了しました: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"動画作成中にエラーが発生: {str(e)}")
            return None


if __name__ == "__main__":
    # テスト用コード
    import sys
    import os
    
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = "これはテスト動画です。"
    
    # 字幕テスト用データ
    test_subtitle = "自分を信じて\n一歩前に進もう\n天才よりも努力する凛凛たる凶器"
    
    creator = VideoCreator()
    
    # 出力ファイルのパスを設定
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    # 字幕ありまたはなしのテストを選択
    if len(sys.argv) > 2 and sys.argv[2] == "with_subtitles":
        print("字幕つき動画を作成しています...")
        print(f"字幕内容: \n{test_subtitle}")
        output_path = os.path.join(output_dir, "test_with_subtitles.mp4")
        result = creator.create_video(
            text, 
            output_path=output_path,
            subtitles=test_subtitle,  # 字幕テキストを渡す
            mute_audio=True,
            skip_text=True  # メインテキストは表示せず、字幕のみ表示
        )
        print("字幕つき動画を作成しています...")
        print(f"字幕内容: \n{test_subtitle}")
    else:
        print("通常動画を作成しています...")
        output_path = os.path.join(output_dir, "test_video.mp4")
        result = creator.create_video(
            text, 
            output_path=output_path, 
            mute_audio=True
        )
    
    if result:
        print(f"動画を作成しました: {result}")
    else:
        print("動画の作成に失敗しました")
