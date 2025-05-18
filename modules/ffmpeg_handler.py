#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FFmpegを直接実行して動画を処理するためのモジュール
"""

import os
import subprocess
import logging
import shlex

logger = logging.getLogger('youtube-shorts-bot.ffmpeg_handler')

def run_ffmpeg_command(command, log_output=True):
    """
    FFmpegコマンドを実行する
    
    Args:
        command (list): FFmpegコマンドとその引数のリスト
        log_output (bool): 出力をログに記録するかどうか
        
    Returns:
        bool: コマンドが成功したかどうか
    """
    try:
        logger.info(f"FFmpegコマンドを実行: {' '.join(command)}")
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"FFmpegエラー: {stderr}")
            return False
        
        if log_output and stderr:
            logger.debug(f"FFmpeg出力: {stderr}")
            
        return True
    
    except Exception as e:
        logger.error(f"FFmpeg実行エラー: {e}")
        return False

def add_text_to_video(input_video, output_video, text, font_size=70, font_color="white", bg_opacity=0.5):
    """
    動画に直接テキストを描画する (ハードサブ方式)
    drawtextフィルターを使用して、動画の中央にテキストを描画
    
    Args:
        input_video (str): 入力動画のパス
        output_video (str): 出力動画のパス
        text (str): 表示するテキスト
        font_size (int): フォントサイズ
        font_color (str): フォント色(「white」, 「yellow」など)
        bg_opacity (float): 背景の不透明度(0.0～1.0)
        
    Returns:
        bool: 成功したかどうか
    """
    # テキストを行ごとに分割
    lines = text.strip().split('\n')
    
    # 各行のdrawtextフィルターを作成
    drawtext_filters = []
    
    # 各行のdrawtextフィルターを生成
    y_offset = -100  # 最初の行は中央より少し上に配置
    line_spacing = font_size * 1.5  # 行間
    
    for i, line in enumerate(lines):
        # テキストをエスケープ
        escaped_line = line.replace("'", "\\'").replace(':', '\\:')
        
        # y位置は中央からの相対位置
        y_pos = f"(h/2)+{y_offset+i*line_spacing}"
        
        # 各行のドローテキストフィルター
        # 黒い背景を追加して読みやすくする
        filter_line = (
            f"drawtext=text='{escaped_line}':fontsize={font_size}:fontcolor={font_color}:"
            f"x=(w-text_w)/2:y={y_pos}:shadowcolor=black:shadowx=2:shadowy=2:"
            f"box=1:boxcolor=black@{bg_opacity}:boxborderw=10"
        )
        drawtext_filters.append(filter_line)
    
    # 全てのフィルターを連結
    filter_complex = ','.join(drawtext_filters)
    
    # FFmpegコマンドの構築
    command = [
        "ffmpeg",
        "-i", input_video,
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "copy" if os.path.exists(input_video) else "-an",
        "-y",  # 既存ファイルを上書き
        output_video
    ]
    
    logger.info(f"テキスト描画フィルター: {filter_complex}")
    return run_ffmpeg_command(command)


# 元の関数名を維持するためのエイリアス
add_subtitles_to_video = add_text_to_video

def convert_to_vertical(input_video, output_video, target_width=1080, target_height=1920):
    """
    動画を縦長形式（9:16比率）に変換する
    水平方向にクロップし、縦幅を調整して適切な比率にする
    
    Args:
        input_video (str): 入力動画のパス
        output_video (str): 出力動画のパス
        target_width (int): 出力動画の幅
        target_height (int): 出力動画の高さ
        
    Returns:
        bool: 成功したかどうか
    """
    # 入力動画の情報を取得
    probe_cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0:s=x",
        input_video
    ]
    
    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        source_width, source_height = map(int, result.stdout.strip().split('x'))
        logger.info(f"元の動画サイズ: {source_width}x{source_height}")
    except Exception as e:
        logger.error(f"動画情報取得エラー: {e}")
        return False
    
    # アスペクト比を計算
    source_aspect = source_width / source_height
    target_aspect = target_width / target_height  # 9:16 = 0.5625
    
    # 2つの方法から選択
    if source_width >= source_height:  # 横長動画の場合
        # 方法１：クロップしてからスケール
        # 水平方向にクロップしてスクエアに近い形状にする
        crop_height = source_height
        crop_width = int(crop_height * target_aspect)
        
        # クロップ位置は中央
        x_offset = int((source_width - crop_width) / 2)
        
        # フィルター文字列を作成
        filter_complex = f"crop={crop_width}:{crop_height}:{x_offset}:0,scale={target_width}:{target_height}"
    else:  # 縦長動画の場合
        # 方法２：直接スケールを適用し、上下に黒いバーを付ける
        if source_aspect < target_aspect:
            # 入力がターゲットよりも縦長の場合は幅に合わせる
            scaled_width = target_width
            scaled_height = int(scaled_width / source_aspect)
            y_padding = int((target_height - scaled_height) / 2)
            filter_complex = f"scale={scaled_width}:{scaled_height},pad={target_width}:{target_height}:0:{y_padding}:black"
        else:
            # それ以外は高さに合わせる
            scaled_height = target_height
            scaled_width = int(scaled_height * source_aspect)
            x_padding = int((target_width - scaled_width) / 2)
            filter_complex = f"scale={scaled_width}:{scaled_height},pad={target_width}:{target_height}:{x_padding}:0:black"
    
    # コマンドを構築
    command = [
        "ffmpeg",
        "-i", input_video,
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "copy" if os.path.exists(input_video) else "-an",
        "-y",
        output_video
    ]
    
    logger.info(f"縦長動画変換フィルター: {filter_complex}")
    return run_ffmpeg_command(command)


# 目的のために元の関数名を導入するようにエイリアスを定義
crop_video = convert_to_vertical

def trim_video(input_video, output_video, start_time=0, duration=None):
    """
    動画をトリムする（長さを調整する）
    
    Args:
        input_video (str): 入力動画のパス
        output_video (str): 出力動画のパス
        start_time (float): 開始時間（秒）
        duration (float): 動画の長さ（秒）。Noneの場合は最後まで
        
    Returns:
        bool: 成功したかどうか
    """
    # コマンドの構築
    command = [
        "ffmpeg",
        "-i", input_video,
        "-ss", str(start_time)
    ]
    
    # 期間が指定されている場合
    if duration is not None:
        command.extend(["-t", str(duration)])
    
    # 出力設定
    command.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "copy" if os.path.exists(input_video) else "-an",
        "-y",
        output_video
    ])
    
    return run_ffmpeg_command(command)

def mute_video(input_video, output_video):
    """
    動画の音声をミュートする
    
    Args:
        input_video (str): 入力動画のパス
        output_video (str): 出力動画のパス
        
    Returns:
        bool: 成功したかどうか
    """
    command = [
        "ffmpeg",
        "-i", input_video,
        "-c:v", "copy",
        "-an",  # 音声を削除
        "-y",
        output_video
    ]
    
    return run_ffmpeg_command(command)
