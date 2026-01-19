# YouTube Frame Extractor

Tool trích xuất khung hình (frame) từ video YouTube tại các mốc thời gian cụ thể.

## Yêu cầu hệ thống

- **Hệ điều hành**: Linux (Ubuntu)
- **Python**: 3.6+
- **ffmpeg**: Xử lý video
- **yt-dlp**: Tải video từ YouTube

## Cài đặt

### Bước 1: Cài đặt ffmpeg

```bash
sudo apt update
sudo apt install ffmpeg
```

### Bước 2: Cài đặt yt-dlp

```bash
pip3 install yt-dlp
```

Hoặc cài từ requirements.txt:

```bash
pip3 install -r requirements.txt
```

## Cách sử dụng

### Chạy script

```bash
python3 youtube_frame_extractor.py
```

### Các bước thực hiện

1. **Nhập link YouTube**: Dán link video YouTube vào (hỗ trợ cả link ngắn youtu.be)

2. **Nhập mốc thời gian**: 
   - Định dạng: `MM:SS` hoặc `HH:MM:SS`
   - Nhập nhiều mốc cách nhau bằng dấu phẩy
   - Ví dụ: `02:30, 05:10, 10:00`

3. **Chờ xử lý**: Tool sẽ tự động trích xuất frame tại các mốc thời gian

4. **Lấy kết quả**: Các file ảnh được lưu trong thư mục `output/`

## Ví dụ

```
============================================================
       YOUTUBE FRAME EXTRACTOR
       Trích xuất khung hình từ video YouTube
============================================================

✅ Tất cả dependencies đã được cài đặt.

🔗 Nhập link YouTube: https://www.youtube.com/watch?v=dQw4w9WgXcQ

⏱️  Nhập các mốc thời gian (định dạng MM:SS hoặc HH:MM:SS)
   Có thể nhập nhiều mốc, cách nhau bằng dấu phẩy
   Ví dụ: 02:30, 05:10, 10:00

   Các mốc thời gian: 00:30, 01:00, 02:00

📋 Sẽ trích xuất 3 frame: 00:30, 01:00, 02:00

🔍 Đang lấy thông tin video từ YouTube...
✅ Đã lấy được stream URL.

🎬 Bắt đầu trích xuất frames...
----------------------------------------
📸 Đang trích xuất frame tại 00:30 (30.0s)...
   ✅ Đã lưu: screenshot_00-30.png
📸 Đang trích xuất frame tại 01:00 (60.0s)...
   ✅ Đã lưu: screenshot_01-00.png
📸 Đang trích xuất frame tại 02:00 (120.0s)...
   ✅ Đã lưu: screenshot_02-00.png
----------------------------------------

============================================================
✨ HOÀN THÀNH!
   Đã trích xuất: 3/3 frames
   Thư mục đầu ra: /path/to/output

📁 Các file đã tạo:
   - screenshot_00-30.png
   - screenshot_01-00.png
   - screenshot_02-00.png
============================================================
```

## Đầu ra

- **Định dạng ảnh**: PNG
- **Tên file**: `screenshot_MM-SS.png` (ví dụ: `screenshot_02-30.png`)
- **Thư mục**: `output/`

## Xử lý lỗi

| Lỗi | Giải pháp |
|-----|-----------|
| `ffmpeg not found` | Chạy `sudo apt install ffmpeg` |
| `yt-dlp not found` | Chạy `pip3 install yt-dlp` |
| `Không lấy được video` | Kiểm tra link YouTube có hợp lệ và không bị giới hạn |
| `Frame không đúng` | Đảm bảo timestamp không vượt quá độ dài video |

## Ghi chú

- Tool hỗ trợ video công khai và không giới hạn truy cập
- Thời gian xử lý phụ thuộc vào tốc độ mạng và độ dài video
- Mỗi frame được trích xuất chính xác tại thời điểm chỉ định
