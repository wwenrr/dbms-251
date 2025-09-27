# 🏥 HỆ THỐNG CƠ SỞ DỮ LIỆU MRI

## 🚀 Cách chạy hệ thống

### 1. Khởi động Redis
```bash
# Windows
redis-server

# Linux/Mac
sudo systemctl start redis
```

### 2. Chạy hệ thống chính
```bash
python interactive_menu.py
```

## 📋 Các chức năng chính

### 1. 🔍 Tìm thông tin bệnh nhân khi biết ID
- Nhập Patient ID để xem thông tin và ảnh MRI
- Xem chi tiết từng ảnh
- Tìm kiếm bệnh nhân khác

### 2. 🔍 Tìm bệnh nhân với bộ lọc
- Nhập Patient ID và các điều kiện lọc
- Lọc theo: series description, modality, manufacturer, giới tính, tuổi
- Xem kết quả khớp với điều kiện

### 3. 🔍 Tìm ảnh MRI tương tự
- Nhập Patient ID và chỉ số ảnh tham chiếu
- Tìm ảnh tương tự từ các bệnh nhân khác
- Xem độ tương tự và thông tin chi tiết

### 4. 🎯 Demo tất cả API
- Chạy thử tất cả các chức năng
- Xem ví dụ sử dụng từng API

## 🔧 Các file chính

- `interactive_menu.py` - Menu chính
- `interactive_case_1.py` - Case Study 1
- `interactive_case_2.py` - Case Study 2  
- `interactive_case_3.py` - Case Study 3
- `demo_all_apis.py` - Demo tất cả API
- `api_case_1.py` - API Case Study 1
- `api_case_2.py` - API Case Study 2
- `api_case_3.py` - API Case Study 3

## 📊 Dữ liệu

- Dữ liệu MRI được lưu trong thư mục `data/`
- Metadata được lưu trong Redis
- Hỗ trợ định dạng DICOM (.ima files)

## 🎯 Sử dụng

1. Chạy `python interactive_menu.py`
2. Chọn chức năng từ menu (1-5)
3. Làm theo hướng dẫn trên màn hình
4. Nhập 'quit' để thoát bất cứ lúc nào
