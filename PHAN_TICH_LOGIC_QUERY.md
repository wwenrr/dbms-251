# 🔍 PHÂN TÍCH LOGIC QUERY - HỆ THỐNG MRI DATABASE

## 📊 Tổng quan hệ thống

Hệ thống sử dụng **Redis** làm database chính để lưu trữ metadata của ảnh MRI và thông tin bệnh nhân.

---

## 🗂️ Cấu trúc dữ liệu trong Redis

### 1. **Patient Data** (Dữ liệu bệnh nhân)
```
Key: patient:{patient_id}
Value: JSON string
Ví dụ: patient:70 → {"notes": "Clinical notes here..."}
```

### 2. **Image Metadata** (Metadata ảnh)
```
Key: metadata:{patient_id}:{image_index}
Value: JSON string
Ví dụ: metadata:70:0 → {"SeriesDescription": "T1_TSE_SAG", "Modality": "MR", ...}
```

---

## 🔍 CASE STUDY 1: Basic Patient Lookup

### **Mục đích:** Tìm thông tin bệnh nhân và tất cả ảnh MRI khi biết Patient ID

### **Logic Query:**

#### **Bước 1: Lấy thông tin bệnh nhân**
```python
patient_key = f"patient:{patient_id}"
patient_data = self.client.get(patient_key)
```
- **Query:** `GET patient:70`
- **Mục đích:** Lấy ghi chú lâm sàng của bệnh nhân
- **Kết quả:** JSON chứa `notes` field

#### **Bước 2: Lấy tất cả metadata ảnh**
```python
pattern = f"metadata:{patient_id}:*"
keys = self.client.keys(pattern)
```
- **Query:** `KEYS metadata:70:*`
- **Mục đích:** Tìm tất cả ảnh của bệnh nhân
- **Kết quả:** Danh sách keys như `metadata:70:0`, `metadata:70:1`, ...

#### **Bước 3: Xử lý từng ảnh**
```python
for key in keys:
    metadata = self.client.get(key)
    img_data = json.loads(metadata)
```
- **Query:** `GET metadata:70:0`, `GET metadata:70:1`, ...
- **Mục đích:** Lấy thông tin chi tiết từng ảnh
- **Kết quả:** JSON chứa SeriesDescription, Modality, Manufacturer, ...

### **Độ phức tạp:**
- **Time Complexity:** O(n) với n = số ảnh của bệnh nhân
- **Space Complexity:** O(n) để lưu danh sách ảnh

---

## 🔍 CASE STUDY 2: Patient + Conditions

### **Mục đích:** Tìm ảnh MRI phù hợp với điều kiện cụ thể

### **Logic Query:**

#### **Bước 1-2:** Giống Case Study 1 (lấy patient info + metadata)

#### **Bước 3: Lọc theo điều kiện**
```python
def _matches_conditions(self, img_data: Dict, conditions: Dict[str, str]) -> bool:
    for field, value in conditions.items():
        # Map field names
        field_mapping = {
            'series_description': 'SeriesDescription',
            'modality': 'Modality', 
            'manufacturer': 'Manufacturer',
            'patient_sex': 'PatientSex',
            'patient_age': 'PatientAge'
        }
        
        actual_field = field_mapping.get(field, field)
        img_value = str(img_data[actual_field]).lower()
        search_value = str(value).lower()
        
        if search_value not in img_value:
            return False
    return True
```

### **Các loại điều kiện hỗ trợ:**

#### **1. Series Description Filter**
```python
conditions = {"series_description": "t2"}
# Tìm ảnh có SeriesDescription chứa "t2"
```

#### **2. Modality Filter**
```python
conditions = {"modality": "MR"}
# Tìm ảnh có Modality = "MR"
```

#### **3. Manufacturer Filter**
```python
conditions = {"manufacturer": "SIEMENS"}
# Tìm ảnh có Manufacturer = "SIEMENS"
```

#### **4. Patient Demographics**
```python
conditions = {"patient_sex": "M", "patient_age": "30Y"}
# Tìm ảnh của bệnh nhân nam, 30 tuổi
```

#### **5. Combined Filters**
```python
conditions = {"series_description": "t2", "modality": "MR"}
# Tìm ảnh T2-weighted MR
```

### **Độ phức tạp:**
- **Time Complexity:** O(n × m) với n = số ảnh, m = số điều kiện
- **Filtering:** Case-insensitive partial matching

---

## 🔍 CASE STUDY 3: Similar Images

### **Mục đích:** Tìm ảnh tương tự với ảnh tham chiếu

### **Logic Query:**

#### **Bước 1: Lấy ảnh tham chiếu**
```python
pattern = f"metadata:{patient_id}:*"
keys = self.client.keys(pattern)
key = keys[image_index]  # Lấy ảnh theo index
metadata = self.client.get(key)
```

#### **Bước 2: Lấy tất cả metadata từ tất cả patients**
```python
all_keys = self.client.keys("metadata:*:*")
all_data = []

for key in all_keys:
    result = self.client.get(key)
    if result:
        all_data.append(json.loads(result))
```

#### **Bước 3: Tính độ tương tự**
```python
def _calculate_similarity(self, ref_image: Dict, img_data: Dict, comparison_fields: List[str]) -> float:
    score = 0
    total_fields = 0
    
    for field in comparison_fields:
        ref_value = ref_image.get(field, '')
        img_value = img_data.get(field, '')
        
        if ref_value and img_value:
            total_fields += 1
            
            # Exact match
            if ref_value == img_value:
                score += 1
            # Partial match for series description
            elif field == 'SeriesDescription':
                ref_words = set(str(ref_value).lower().split())
                img_words = set(str(img_value).lower().split())
                common_words = ref_words.intersection(img_words)
                if common_words:
                    score += len(common_words) / max(len(ref_words), len(img_words))
    
    return score / total_fields if total_fields > 0 else 0
```

### **Các trường so sánh:**
- **SeriesDescription:** Exact + partial match (từ khóa chung)
- **Modality:** Exact match
- **Manufacturer:** Exact match  
- **SliceThickness:** Exact match
- **MagneticFieldStrength:** Exact match

### **Độ phức tạp:**
- **Time Complexity:** O(n × m) với n = tổng số ảnh, m = số trường so sánh
- **Space Complexity:** O(n) để lưu tất cả metadata

---

## 🗂️ Cấu trúc file ảnh

### **Đường dẫn ảnh:**
```
data/image_data/01_MRI_Data/
├── 0021/  # Patient ID (zero-padded)
│   └── L-SPINE_LSS_20160102_131621_669000/
│       └── T1_TSE_SAG_320_0003/
│           └── T1_TSE_SAG__0021_001.ima
```

### **Logic tìm file:**
```python
def _get_image_path(self, img_data: Dict) -> str:
    patient_id = img_data.get('patient_id', '')
    series_desc = img_data.get('SeriesDescription', '')
    
    base_path = f"{self.image_base_path}/{patient_id.zfill(4)}"
    
    # Tìm thư mục L-SPINE_LSS_*
    for subdir in os.listdir(base_path):
        if subdir.startswith("L-SPINE_LSS_"):
            # Tìm thư mục series phù hợp
            series_dirs = [d for d in os.listdir(os.path.join(base_path, subdir)) 
                         if series_desc.replace(' ', '_').upper() in d.upper()]
            if series_dirs:
                series_path = os.path.join(base_path, subdir, series_dirs[0])
                # Tìm file .ima
                for f in os.listdir(series_path):
                    if f.endswith('.ima') and patient_id.zfill(4) in f:
                        return os.path.join(series_path, f)
```

---

## 📊 Performance Analysis

### **Redis Operations:**

#### **Case Study 1:**
- `GET patient:{id}` - O(1)
- `KEYS metadata:{id}:*` - O(N) với N = số keys
- `GET metadata:{id}:{index}` - O(1) × n lần

#### **Case Study 2:**
- Giống Case Study 1 + filtering logic
- Thêm O(n × m) cho filtering

#### **Case Study 3:**
- `KEYS metadata:*:*` - O(N) với N = tổng số keys
- `GET metadata:*:*` - O(1) × N lần
- Similarity calculation - O(N × m)

### **Memory Usage:**
- **Case Study 1:** O(n) với n = số ảnh của patient
- **Case Study 2:** O(n) với n = số ảnh khớp
- **Case Study 3:** O(N) với N = tổng số ảnh trong hệ thống

---

## 🔧 Optimization Suggestions

### **1. Indexing:**
```python
# Có thể thêm secondary indexes
# SET series:t2:patients {patient_ids}
# SET modality:MR:patients {patient_ids}
```

### **2. Caching:**
```python
# Cache kết quả similarity calculation
# HSET similarity:{ref_id}:{img_id} score
```

### **3. Pagination:**
```python
# Thay vì lấy tất cả metadata, có thể paginate
# SCAN cursor MATCH metadata:*:* COUNT 100
```

---

## 🎯 Kết luận

Hệ thống sử dụng **Redis** hiệu quả với:
- **Simple key-value storage** cho patient data
- **Pattern-based keys** cho metadata
- **In-memory filtering** cho conditions
- **Similarity scoring** cho image matching

**Ưu điểm:**
- ✅ Fast lookups (O(1) cho GET operations)
- ✅ Flexible filtering
- ✅ Easy to scale

**Nhược điểm:**
- ❌ KEYS operation có thể chậm với large datasets
- ❌ Similarity calculation tốn CPU
- ❌ Memory usage cao cho Case Study 3
