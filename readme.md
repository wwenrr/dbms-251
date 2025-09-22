## Mô tả dự án

Pipeline nhỏ xử lý dữ liệu MRI:
- Tải tập dữ liệu văn bản (Excel/CSV) và ảnh (ZIP) từ nguồn công khai.
- Parse metadata từ các file ảnh MRI (.ima) thành JSON.
- Ghi chú lâm sàng và metadata được nạp vào Redis để tra cứu nhanh.

## Hướng dẫn (Windows, PowerShell)

Scripts nằm trong `scripts/win`:
- `install.ps1`: cài thư viện. Có thể truyền tên gói để cài thêm.
	- Không tham số: cài theo `req.txt` và tạo `venv` nếu thiếu.
	- Có tham số: `./scripts/win/install.ps1 requests` sẽ cài thêm gói và cập nhật `req.txt`.
- `run.ps1`: chạy CLI của dự án (`src/run.py`). Có thể truyền lệnh phía sau.
- `debug.ps1`: chạy ở chế độ gỡ lỗi (pdb).

Yêu cầu:
- Redis đang chạy (có thể dùng Docker: `docker-compose up -d`). Mặc định kết nối `localhost:6379`.
- Python trong `venv` được tạo bởi `install.ps1` (script tự kiểm tra phiên bản Python trong venv).

Các lệnh CLI (`./scripts/win/run.ps1 <command>`):
- `download`: tải dữ liệu văn bản và ảnh về thư mục `data/`.
- `parse`: đọc ảnh `.ima` trong `data/image_data/01_MRI_DATA` và xuất metadata JSON vào `data/metadata/`.
- `insert`: đọc `data/text_data.csv` và `data/metadata/*.json`, sau đó ghi vào Redis.
- `clean`: xóa sạch dữ liệu trong Redis DB hiện tại.

Lưu ý khi chạy `run` kèm tên command:
- Ví dụ: `./scripts/win/run.ps1 download`; `./scripts/win/run.ps1 parse`; `./scripts/win/run.ps1 insert`.
- `insert` sẽ báo lỗi nếu chưa có `data/` hoặc chưa `parse` để tạo `data/metadata/`.

## Thứ tự khuyến nghị
1) `download` (tải dữ liệu trước)
2) `parse` (parse metadata)
3) `insert` (nạp dữ liệu vào Redis)

Kiểm thử lại: nhớ chạy `clean` để dọn dữ liệu Redis trước khi nạp lại.

## Gợi ý nhanh
- Khởi động Redis bằng Docker: `docker-compose up -d` (cổng 6379, UI RedisInsight: 8001).
- Dữ liệu sau khi tải nằm ở `data/` (Excel sẽ được chuyển sang `text_data.csv`).
