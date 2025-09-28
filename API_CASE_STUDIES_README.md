# MRI Database - 3 Case Studies API

Hệ thống API cho 3 case studies của Lumbar Spine MRI Dataset.

## 🚀 Quick Start

### 1. Chạy demo tổng hợp
```bash
python demo_all_apis.py
```

### 2. Test từng API riêng lẻ
```bash
python api_case_1.py    # Case Study 1
python api_case_2.py    # Case Study 2  
python api_case_3.py    # Case Study 3
```

## 📋 API Documentation

### 🔧 Case Study 1: Basic Patient Lookup
**File:** `api_case_1.py`  
**Class:** `Case1API`

**Mô tả:** Truy xuất văn bản và ảnh khi biết patient ID

**Input:**
- `patient_id` (string): ID của bệnh nhân (ví dụ: "70", "1", "2")

**Output:**
```python
{
    'success': True/False,
    'patient_id': '70',
    'clinical_notes': 'L5-S1: Diffuse disc bulge...',
    'mri_images': [
        {
            'image_index': 0,
            'series_description': 't1_tse_tra',
            'modality': 'MR',
            'manufacturer': 'SIEMENS',
            'patient_age': '019Y',
            'patient_sex': 'M',
            'file_path': 'data/image_data/...',
            'file_exists': True/False
        }
    ],
    'total_images': 73
}
```

**Usage:**
```python
from api_case_1 import Case1API
api = Case1API()
result = api.get_patient_data('70')
```

---

### 🔧 Case Study 2: Patient + Conditions
**File:** `api_case_2.py`  
**Class:** `Case2API`

**Mô tả:** Truy xuất văn bản và ảnh khi biết patient ID + điều kiện cụ thể

**Input:**
- `patient_id` (string): ID của bệnh nhân
- `conditions` (dict): Điều kiện lọc

**Available Conditions:**
```python
{
    'series_description': 't2',        # Tìm series chứa "t2"
    'modality': 'MR',                  # Tìm modality = "MR"
    'manufacturer': 'SIEMENS',         # Tìm manufacturer = "SIEMENS"
    'patient_sex': 'M',                # Tìm giới tính nam
    'patient_age': '019Y'              # Tìm tuổi cụ thể
}
```

**Output:**
```python
{
    'success': True/False,
    'patient_id': '70',
    'conditions': {'series_description': 't2'},
    'clinical_notes': 'L5-S1: Diffuse disc bulge...',
    'matching_images': [...],
    'total_matching_images': 34,
    'total_patient_images': 73,
    'match_percentage': 46.6
}
```

**Usage:**
```python
from api_case_2 import Case2API
api = Case2API()
result = api.get_patient_with_conditions('70', {'series_description': 't2'})
```

---

### 🔧 Case Study 3: Similar Images
**File:** `api_case_3.py`  
**Class:** `Case3API`

**Mô tả:** Truy xuất ảnh MRI tương tự với một ảnh MRI đã cho

**Input:**
- `reference_patient_id` (string): ID của bệnh nhân tham chiếu
- `reference_image_index` (int): Index của ảnh tham chiếu (0, 1, 2...)
- `top_n` (int): Số lượng ảnh tương tự tối đa (mặc định: 10)

**Output:**
```python
{
    'success': True/False,
    'reference_image': {
        'patient_id': '70',
        'image_index': 0,
        'series_description': 't1_tse_tra',
        'modality': 'MR',
        'manufacturer': 'SIEMENS'
    },
    'similar_images': [
        {
            'patient_id': '126',
            'image_index': 0,
            'series_description': 't1_tse_tra',
            'similarity_score': 1.00,
            'modality': 'MR'
        }
    ],
    'total_similar': 5
}
```

**Usage:**
```python
from api_case_3 import Case3API
api = Case3API()
result = api.find_similar_images('70', 0, 5)
```

## 🔍 Similarity Criteria (Case Study 3)

API sử dụng các tiêu chí sau để tính độ tương tự:

1. **SeriesDescription** (exact + partial match)
2. **Modality** (exact match)
3. **Manufacturer** (exact match)
4. **SliceThickness** (exact match)
5. **MagneticFieldStrength** (exact match)

## 📊 Dataset Information

- **Total Patients:** 575
- **Total Images:** 48,345
- **Top Series:** `t2_tse_tra_384`, `t1_tse_tra`, `t2_tse_sag_384`

## 🏥 Medical Context

### Series Types:
- **T1-weighted:** Hiển thị cấu trúc giải phẫu
- **T2-weighted:** Hiển thị chất lỏng và bệnh lý
- **Localizer:** Ảnh định vị để xác định vùng chụp

### Common Conditions:
- Disc bulge (phình đĩa đệm)
- Thecal sac compression (chèn ép túi màng cứng)
- Nerve root compression (chèn ép rễ thần kinh)

## 🚨 Error Handling

Tất cả API trả về format:
```python
{
    'success': True/False,
    'error': 'error message if success=False',
    'data': 'actual data if success=True'
}
```

## 📝 Notes

- Tất cả API sử dụng Redis để lưu trữ dữ liệu
- File paths được tạo tự động từ metadata
- API được thiết kế để dễ dàng tích hợp với frontend
- Case Study 3 sử dụng similarity search dựa trên metadata

