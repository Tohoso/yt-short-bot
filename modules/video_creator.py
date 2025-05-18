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
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# 親ディレクトリをインポートパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

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
    
    def create_text_clip(self, text, duration=None):
        """
        テキストクリップを作成する
        
        Args:
            text (str): 表示するテキスト
            duration (float, optional): クリップの長さ（秒）
            
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
        
        # 中央に配置
        text_clip = text_clip.set_position('center')
        
        return text_clip
    
    def create_video(self, text, output_name=None, skip_text=False, use_original_duration=False):
        """
        テキストと背景動画を組み合わせて動画を作成する
        
        Args:
            text (str): 表示するテキスト
            output_name (str, optional): 出力ファイル名（拡張子なし）
            skip_text (bool, optional): Trueの場合、テキスト表示をスキップします（テスト用）
            use_original_duration (bool, optional): Trueの場合、背景動画の長さをそのまま使用します
            
        Returns:
            str: 作成された動画のパス、失敗した場合はNone
        """
        try:
            # 背景動画取得
            background_path = self.get_random_background()
            if not background_path:
                return None
            
            # 出力ファイル名
            if not output_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"short_{timestamp}"
            
            output_path = os.path.join(self.output_dir, f"{output_name}.mp4")
            
            # 背景動画のクリップ作成
            background_clip = VideoFileClip(background_path).resize(height=config.VIDEO_HEIGHT)
            
            # 背景動画の中央部分をクロップして縦長に
            background_clip = background_clip.crop(
                x_center=background_clip.w/2,
                y_center=background_clip.h/2,
                width=config.VIDEO_WIDTH,
                height=config.VIDEO_HEIGHT
            )
            
            # オリジナルの背景動画の長さを保存
            original_duration = background_clip.duration
            
            # テスト用：背景動画の元の長さを使用する場合
            if use_original_duration:
                # 元の長さから少し短くして安全マージンを確保
                safe_duration = original_duration - 0.2  # 0.2秒の安全マージン
                background_clip = background_clip.subclip(0, safe_duration)
                logger.info(f"背景動画の元の長さを使用: {safe_duration}秒")
            # 通常の場合は設定された長さに合わせる
            elif original_duration < config.VIDEO_DURATION:
                # 短い場合はループする
                n_loops = math.ceil(config.VIDEO_DURATION / original_duration)
                background_clip = background_clip.loop(n=n_loops)
                # 安全マージンをサブクリップに反映
                safe_duration = min(config.VIDEO_DURATION, background_clip.duration - 0.5)
                background_clip = background_clip.subclip(0, safe_duration)
            else:
                # 背景動画が十分長い場合は元の設定通りにクリップ
                background_clip = background_clip.subclip(0, config.VIDEO_DURATION)
            
            # テキスト表示をスキップする場合
            if skip_text:
                final_clip = background_clip
            else:
                # テキストクリップ作成
                text_clip = self.create_text_clip(text, config.VIDEO_DURATION)
                # 合成
                final_clip = CompositeVideoClip([background_clip, text_clip])
            
            # 書き出し
            logger.info(f"動画の書き出し開始: {output_path}")
            final_clip.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=os.path.join(self.temp_dir, 'temp_audio.m4a'),
                remove_temp=True,
                threads=4,
                preset='ultrafast'  # 高速書き出し（品質は低い）
            )
            
            # クリップを閉じる
            background_clip.close()
            if not skip_text:
                text_clip.close()
            final_clip.close()
            
            logger.info(f"動画の書き出し完了: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"動画作成中にエラーが発生: {str(e)}")
            return None


if __name__ == "__main__":
    # テスト用コード
    import sys
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = "これはテスト動画です。背景に文字が表示されます。"
    
    creator = VideoCreator()
    output_path = creator.create_video(text)
    
    print(f"動画を作成しました: {output_path if output_path else '失敗'}")
