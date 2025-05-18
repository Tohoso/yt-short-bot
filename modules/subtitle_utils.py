#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字幕ファイル生成と変換のためのユーティリティ
SRTファイル生成と字幕処理のための機能を提供
"""

import os
import datetime

def create_srt_content(text_lines, video_duration=6, display_entire_duration=True):
    """
    テキスト行からSRTファイルの内容を生成
    
    Args:
        text_lines (list): 字幕として表示するテキスト行のリスト
        video_duration (float): 動画の総再生時間（秒）
        display_entire_duration (bool): 全てのテキストを動画全体に表示するか
        
    Returns:
        str: SRTファイルの内容
    """
    if isinstance(text_lines, str):
        # 文字列の場合は行に分割
        text_lines = text_lines.strip().split('\n')
    
    # 空の行を削除
    text_lines = [line for line in text_lines if line.strip()]
    
    if not text_lines:
        return ""
    
    srt_content = []
    
    if display_entire_duration:
        # 全てのテキストを動画の最初から最後まで表示
        start_time = "00:00:00,000"
        end_time = _format_time(video_duration)
        
        # 全ての行を一つの字幕として表示
        srt_content.append(f"1\n{start_time} --> {end_time}\n{_format_srt_text(text_lines)}\n")
    else:
        # 各行を均等に分割して表示（複数の字幕として）
        line_count = len(text_lines)
        segment_duration = video_duration / line_count
        
        for i, line in enumerate(text_lines):
            start_seconds = i * segment_duration
            end_seconds = (i + 1) * segment_duration
            
            start_time = _format_time(start_seconds)
            end_time = _format_time(end_seconds)
            
            srt_content.append(f"{i+1}\n{start_time} --> {end_time}\n{line}\n")
    
    return "\n".join(srt_content)

def _format_time(seconds):
    """秒数をSRT形式の時間文字列（00:00:00,000）に変換"""
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    seconds %= 60
    hours = minutes // 60
    minutes %= 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def _format_srt_text(text_lines):
    """複数行のテキストをSRT形式に整形"""
    if isinstance(text_lines, list):
        return "\n".join(text_lines)
    return text_lines

def write_srt_file(text, output_path, video_duration=6):
    """
    テキストからSRTファイルを生成して保存
    
    Args:
        text (str or list): 字幕として表示するテキスト（文字列または行のリスト）
        output_path (str): 出力するSRTファイルのパス
        video_duration (float): 動画の総再生時間（秒）
        
    Returns:
        str: 作成されたSRTファイルのパス
    """
    srt_content = create_srt_content(text, video_duration)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    
    return output_path

def get_ffmpeg_subtitle_args(srt_file, font_size=24, font_color="white", bg_opacity=0.5):
    """
    FFmpegの字幕表示用の引数を生成
    
    Args:
        srt_file (str): SRTファイルのパス
        font_size (int): フォントサイズ
        font_color (str): フォント色
        bg_opacity (float): 背景の不透明度（0.0～1.0）
        
    Returns:
        list: FFmpeg用の引数リスト
    """
    # 背景色の設定（不透明度付きの黒）
    bg_color = f"0x000000@{bg_opacity}"
    
    # 字幕用のフィルターを生成
    subtitle_filter = (
        f"subtitles={srt_file}:force_style='Fontsize={font_size},"
        f"PrimaryColour={font_color},BackColour={bg_color},"
        f"Alignment=10,BorderStyle=4'"
    )
    
    return ["-vf", subtitle_filter]
