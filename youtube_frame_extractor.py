#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Frame Extractor (Download Sections Method)
---------------------------------------------------
Tool trích xuất khung hình (frame) từ video YouTube tại các mốc thời gian cụ thể
bằng cách tải các đoạn ngắn quanh timestamp, tránh lỗi 403 từ direct URL.

Yêu cầu:
    - yt-dlp: pip3 install yt-dlp
    - ffmpeg: sudo apt install ffmpeg
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path
from typing import List, Tuple, Optional


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


def seconds_to_timestamp(seconds: float) -> str:
    """
    Chuyển đổi giây sang định dạng HH:MM:SS hoặc MM:SS.
    
    Args:
        seconds: Số giây
    
    Returns:
        Chuỗi timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    else:
        return f"{minutes:02d}:{secs:06.3f}"


def format_timestamp_for_filename(timestamp: str) -> str:
    """
    Chuyển đổi timestamp sang định dạng phù hợp cho tên file.
    Ví dụ: "02:30" -> "02-30"
    """
    return timestamp.strip().replace(':', '-')


def calculate_section(timestamp_seconds: float, pad: float) -> Tuple[float, float]:
    """
    Tính toán khoảng thời gian cần tải.
    
    Args:
        timestamp_seconds: Thời điểm cần trích xuất (giây)
        pad: Khoảng padding (giây)
    
    Returns:
        Tuple (start, end) tính bằng giây
    """
    start = max(0, timestamp_seconds - pad)
    end = timestamp_seconds + pad
    return start, end


def download_section(youtube_url: str, start: float, end: float, 
                     output_path: Path) -> bool:
    """
    Tải một đoạn video ngắn từ YouTube.
    
    Args:
        youtube_url: URL của video YouTube
        start: Thời điểm bắt đầu (giây)
        end: Thời điểm kết thúc (giây)
        output_path: Đường dẫn file đầu ra
    
    Returns:
        True nếu thành công, False nếu thất bại
    """
    start_str = seconds_to_timestamp(start)
    end_str = seconds_to_timestamp(end)
    section_str = f"*{start_str}-{end_str}"
    
    print(f"   📥 Đang tải đoạn {start_str} - {end_str}...")
    
    try:
        subprocess.run([
            'yt-dlp',
            '--download-sections', section_str,
            '--force-keyframes-at-cuts',
            '-f', 'bv*+ba/best',
            '--merge-output-format', 'mp4',
            '-o', str(output_path),
            youtube_url
        ], capture_output=True, text=True, check=True)
        
        if not output_path.exists():
            print(f"   ❌ File không được tạo: {output_path}")
            return False
            
        print(f"   ✅ Đã tải đoạn video")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Lỗi khi tải video:")
        print(f"      {e.stderr}")
        return False


def extract_frame_from_clip(clip_path: Path, offset: float, 
                            output_path: Path) -> bool:
    """
    Trích xuất 1 frame từ video clip tại offset cụ thể.
    
    Args:
        clip_path: Đường dẫn đến file video clip
        offset: Thời điểm cần trích (giây, tính từ đầu clip)
        output_path: Đường dẫn file ảnh đầu ra
    
    Returns:
        True nếu thành công, False nếu thất bại
    """
    print(f"   📸 Đang trích xuất frame tại offset {offset:.2f}s...")
    
    try:
        subprocess.run([
            'ffmpeg',
            '-ss', str(offset),
            '-i', str(clip_path),
            '-frames:v', '1',
            '-q:v', '2',
            '-y',
            str(output_path)
        ], capture_output=True, text=True, check=True)
        
        if not output_path.exists():
            print(f"   ❌ Frame không được tạo")
            return False
            
        print(f"   ✅ Đã lưu frame: {output_path.name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Lỗi khi trích xuất frame:")
        print(f"      {e.stderr}")
        return False


def process_timestamp(youtube_url: str, timestamp: str, pad: float,
                     tmp_dir: Path, output_dir: Path, 
                     keep_temp: bool = False) -> Optional[str]:
    """
    Xử lý một timestamp: tải đoạn video và trích xuất frame.
    
    Args:
        youtube_url: URL của video YouTube
        timestamp: Mốc thời gian (định dạng MM:SS hoặc HH:MM:SS)
        pad: Khoảng padding (giây)
        tmp_dir: Thư mục tạm
        output_dir: Thư mục đầu ra
        keep_temp: Có giữ file tạm không
    
    Returns:
        Đường dẫn file ảnh nếu thành công, None nếu thất bại
    """
    try:
        timestamp_seconds = parse_timestamp(timestamp)
    except ValueError as e:
        print(f"   ❌ {e}")
        return None
    
    # Tính toán section cần tải
    start, end = calculate_section(timestamp_seconds, pad)
    
    # Tên file
    ts_formatted = format_timestamp_for_filename(timestamp)
    clip_filename = f"clip_{ts_formatted}.mp4"
    screenshot_filename = f"screenshot_{ts_formatted}.png"
    
    clip_path = tmp_dir / clip_filename
    screenshot_path = output_dir / screenshot_filename
    
    # Bỏ qua nếu screenshot đã tồn tại
    if screenshot_path.exists():
        print(f"   ⏭️  Screenshot đã tồn tại, bỏ qua: {screenshot_filename}")
        return str(screenshot_path)
    
    # Tải đoạn video
    success = download_section(youtube_url, start, end, clip_path)
    if not success:
        return None
    
    # Trích xuất frame
    offset = timestamp_seconds - start
    success = extract_frame_from_clip(clip_path, offset, screenshot_path)
    
    # Xoá file tạm nếu không giữ
    if not keep_temp and clip_path.exists():
        try:
            clip_path.unlink()
            print(f"   🗑️  Đã xoá file tạm: {clip_filename}")
        except Exception as e:
            print(f"   ⚠️  Không thể xoá file tạm: {e}")
    
    if success:
        return str(screenshot_path)
    return None


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Trích xuất frames từ video YouTube tại các mốc thời gian cụ thể'
    )
    parser.add_argument(
        '--pad',
        type=float,
        default=3.0,
        help='Khoảng padding quanh timestamp (giây), mặc định: 3'
    )
    parser.add_argument(
        '--keep-temp',
        action='store_true',
        help='Giữ các file video tạm'
    )
    return parser.parse_args()


def main():
    """Hàm chính của chương trình."""
    args = parse_arguments()
    
    print("=" * 70)
    print("       YOUTUBE FRAME EXTRACTOR (Download Sections Method)")
    print("       Trích xuất khung hình từ video YouTube")
    print("=" * 70)
    print()
    
    # Kiểm tra dependencies
    check_dependencies()
    print()
    
    # Nhập link YouTube
    youtube_url = input("🔗 Nhập link YouTube: ").strip()
    if not youtube_url:
        print("❌ URL không được để trống.")
        sys.exit(1)
    
    print()
    
    # Nhập danh sách mốc thời gian
    print("⏱️  Nhập các mốc thời gian (định dạng MM:SS hoặc HH:MM:SS)")
    print("   Có thể nhập nhiều mốc, cách nhau bằng dấu phẩy")
    print("   Ví dụ: 00:18, 05:53, 09:02, 17:01, 17:49, 21:59")
    print()
    
    timestamps_input = input("   Các mốc thời gian: ").strip()
    if not timestamps_input:
        print("❌ Vui lòng nhập ít nhất một mốc thời gian.")
        sys.exit(1)
    
    # Parse timestamps
    timestamps = [ts.strip() for ts in timestamps_input.split(',')]
    
    # Loại bỏ trùng lặp
    timestamps = list(dict.fromkeys(timestamps))
    
    print()
    print(f"📋 Cấu hình:")
    print(f"   - Số timestamps: {len(timestamps)}")
    print(f"   - Padding: ±{args.pad}s")
    print(f"   - Giữ file tạm: {'Có' if args.keep_temp else 'Không'}")
    print()
    
    # Tạo thư mục
    tmp_dir = Path("tmp")
    output_dir = Path("output")
    tmp_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Xử lý từng timestamp
    print("🎬 Bắt đầu xử lý timestamps...")
    print("=" * 70)
    
    extracted_files = []
    for i, ts in enumerate(timestamps, 1):
        print(f"\n[{i}/{len(timestamps)}] Timestamp: {ts}")
        print("-" * 70)
        
        result = process_timestamp(
            youtube_url, ts, args.pad, tmp_dir, output_dir, args.keep_temp
        )
        
        if result:
            extracted_files.append(result)
    
    print("\n" + "=" * 70)
    
    # Tổng kết
    print()
    print("=" * 70)
    print(f"✨ HOÀN THÀNH!")
    print(f"   Thành công: {len(extracted_files)}/{len(timestamps)} frames")
    print(f"   Thư mục đầu ra: {output_dir.absolute()}")
    
    if extracted_files:
        print()
        print("📁 Các file đã tạo:")
        for f in extracted_files:
            print(f"   ✓ {Path(f).name}")
    
    if not args.keep_temp:
        print()
        print(f"🗑️  File tạm đã được xoá (thư mục: {tmp_dir.absolute()})")
    else:
        print()
        print(f"📦 File tạm được giữ tại: {tmp_dir.absolute()}")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
