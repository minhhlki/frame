#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Frame Extractor
-----------------------
Tool trích xuất khung hình (frame) từ video YouTube tại các mốc thời gian cụ thể.

Yêu cầu:
    - yt-dlp: pip3 install yt-dlp
    - ffmpeg: sudo apt install ffmpeg
"""

import subprocess
import sys
import os
import re
from pathlib import Path


def check_dependencies():
    """Kiểm tra các dependencies cần thiết."""
    missing = []
    
    # Kiểm tra ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('ffmpeg')
    
    # Kiểm tra yt-dlp
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('yt-dlp')
    
    if missing:
        print("❌ Thiếu các dependencies sau:")
        for dep in missing:
            if dep == 'ffmpeg':
                print(f"   - {dep}: sudo apt install ffmpeg")
            else:
                print(f"   - {dep}: pip3 install {dep}")
        sys.exit(1)
    
    print("✅ Tất cả dependencies đã được cài đặt.")


def parse_timestamp(timestamp: str) -> float:
    """
    Chuyển đổi timestamp từ định dạng MM:SS hoặc HH:MM:SS sang giây.
    
    Args:
        timestamp: Chuỗi thời gian (ví dụ: "02:30" hoặc "01:02:30")
    
    Returns:
        Số giây tương ứng
    """
    timestamp = timestamp.strip()
    parts = timestamp.split(':')
    
    if len(parts) == 2:
        # MM:SS
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    elif len(parts) == 3:
        # HH:MM:SS
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    else:
        raise ValueError(f"Định dạng thời gian không hợp lệ: {timestamp}")


def format_timestamp_for_filename(timestamp: str) -> str:
    """
    Chuyển đổi timestamp sang định dạng phù hợp cho tên file.
    Ví dụ: "02:30" -> "02-30"
    """
    return timestamp.strip().replace(':', '-')


def get_video_stream_url(youtube_url: str) -> str:
    """
    Lấy direct stream URL của video YouTube.
    
    Args:
        youtube_url: URL của video YouTube
    
    Returns:
        Direct stream URL
    """
    print(f"🔍 Đang lấy thông tin video từ YouTube...")
    
    try:
        result = subprocess.run(
            ['yt-dlp', '-f', 'best[ext=mp4]/best', '-g', youtube_url],
            capture_output=True,
            text=True,
            check=True
        )
        stream_url = result.stdout.strip()
        
        if not stream_url:
            raise Exception("Không thể lấy stream URL")
        
        print("✅ Đã lấy được stream URL.")
        return stream_url
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi lấy video: {e.stderr}")
        sys.exit(1)


def extract_frame(stream_url: str, timestamp: str, output_dir: Path) -> str:
    """
    Trích xuất 1 frame tại thời điểm cụ thể.
    
    Args:
        stream_url: Direct stream URL của video
        timestamp: Mốc thời gian (định dạng MM:SS hoặc HH:MM:SS)
        output_dir: Thư mục đầu ra
    
    Returns:
        Đường dẫn file ảnh đã tạo
    """
    seconds = parse_timestamp(timestamp)
    filename = f"screenshot_{format_timestamp_for_filename(timestamp)}.png"
    output_path = output_dir / filename
    
    print(f"📸 Đang trích xuất frame tại {timestamp} ({seconds}s)...")
    
    try:
        # Sử dụng -ss trước input để seek nhanh
        subprocess.run([
            'ffmpeg',
            '-ss', str(seconds),      # Seek đến thời điểm
            '-i', stream_url,          # Input stream
            '-frames:v', '1',          # Chỉ lấy 1 frame
            '-q:v', '2',               # Chất lượng cao
            '-y',                      # Ghi đè nếu file tồn tại
            str(output_path)
        ], capture_output=True, check=True)
        
        print(f"   ✅ Đã lưu: {filename}")
        return str(output_path)
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Lỗi khi trích xuất frame tại {timestamp}: {e.stderr.decode()}")
        return None


def validate_youtube_url(url: str) -> bool:
    """Kiểm tra URL có phải là YouTube không."""
    youtube_patterns = [
        r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(https?://)?(www\.)?youtu\.be/[\w-]+',
        r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+'
    ]
    return any(re.match(pattern, url) for pattern in youtube_patterns)


def main():
    """Hàm chính của chương trình."""
    print("=" * 60)
    print("       YOUTUBE FRAME EXTRACTOR")
    print("       Trích xuất khung hình từ video YouTube")
    print("=" * 60)
    print()
    
    # Kiểm tra dependencies
    check_dependencies()
    print()
    
    # Nhập link YouTube
    while True:
        youtube_url = input("🔗 Nhập link YouTube: ").strip()
        if validate_youtube_url(youtube_url):
            break
        print("❌ URL không hợp lệ. Vui lòng nhập link YouTube.")
    
    print()
    
    # Nhập danh sách mốc thời gian
    print("⏱️  Nhập các mốc thời gian (định dạng MM:SS hoặc HH:MM:SS)")
    print("   Có thể nhập nhiều mốc, cách nhau bằng dấu phẩy")
    print("   Ví dụ: 02:30, 05:10, 10:00")
    print()
    
    while True:
        timestamps_input = input("   Các mốc thời gian: ").strip()
        if timestamps_input:
            break
        print("   ❌ Vui lòng nhập ít nhất một mốc thời gian.")
    
    # Parse timestamps
    timestamps = [ts.strip() for ts in timestamps_input.split(',')]
    
    # Validate timestamps
    valid_timestamps = []
    for ts in timestamps:
        try:
            parse_timestamp(ts)  # Kiểm tra định dạng
            valid_timestamps.append(ts)
        except ValueError as e:
            print(f"   ⚠️  Bỏ qua timestamp không hợp lệ: {ts}")
    
    if not valid_timestamps:
        print("❌ Không có timestamp hợp lệ nào. Thoát chương trình.")
        sys.exit(1)
    
    print()
    print(f"📋 Sẽ trích xuất {len(valid_timestamps)} frame: {', '.join(valid_timestamps)}")
    print()
    
    # Tạo thư mục output
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Lấy stream URL
    stream_url = get_video_stream_url(youtube_url)
    print()
    
    # Trích xuất các frame
    print("🎬 Bắt đầu trích xuất frames...")
    print("-" * 40)
    
    extracted_files = []
    for ts in valid_timestamps:
        result = extract_frame(stream_url, ts, output_dir)
        if result:
            extracted_files.append(result)
    
    print("-" * 40)
    print()
    
    # Tổng kết
    print("=" * 60)
    print(f"✨ HOÀN THÀNH!")
    print(f"   Đã trích xuất: {len(extracted_files)}/{len(valid_timestamps)} frames")
    print(f"   Thư mục đầu ra: {output_dir.absolute()}")
    print()
    print("📁 Các file đã tạo:")
    for f in extracted_files:
        print(f"   - {Path(f).name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
