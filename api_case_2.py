#!/usr/bin/env python3
"""
API Case Study 2: Truy xuất văn bản và ảnh khi biết patient ID + điều kiện cụ thể
"""

import redis
import json
import os
from typing import Dict, Any, List

class Case2API:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)
        self.image_base_path = "data/image_data/01_MRI_Data"
    
    def get_patient_with_conditions(self, patient_id: str, conditions: Dict[str, str]) -> Dict[str, Any]:
        """
        Truy xuất văn bản và ảnh khi biết patient ID + điều kiện cụ thể
        
        Args:
            patient_id (str): ID của bệnh nhân (ví dụ: "70", "1", "2")
            conditions (Dict): Điều kiện lọc, ví dụ:
                - {"series_description": "t2"}  # Tìm series chứa "t2"
                - {"modality": "MR"}            # Tìm modality = "MR"
                - {"manufacturer": "SIEMENS"}   # Tìm manufacturer = "SIEMENS"
                - {"series_description": "sagittal", "modality": "MR"}  # Kết hợp nhiều điều kiện
        
        Returns:
            Dict chứa thông tin bệnh nhân, ghi chú lâm sàng và danh sách ảnh MRI phù hợp
        """
        try:
            result = {
                'success': True,
                'patient_id': patient_id,
                'conditions': conditions,
                'clinical_notes': '',
                'matching_images': [],
                'total_matching_images': 0,
                'total_patient_images': 0,
                'match_percentage': 0.0,
                'error': None
            }
            
            # 1. Lấy ghi chú lâm sàng
            patient_key = f"patient:{patient_id}"
            patient_data = self.client.get(patient_key)
            
            if not patient_data:
                result['success'] = False
                result['error'] = f"Patient {patient_id} not found"
                return result
            
            patient_info = json.loads(patient_data)
            result['clinical_notes'] = patient_info.get('notes', '')
            
            # 2. Lấy tất cả metadata của patient
            pattern = f"metadata:{patient_id}:*"
            keys = self.client.keys(pattern)
            all_images = []
            matching_images = []
            
            for key in keys:
                try:
                    metadata = self.client.get(key)
                    if metadata:
                        img_data = json.loads(metadata)
                        all_images.append(img_data)
                        
                        # Kiểm tra điều kiện
                        if self._matches_conditions(img_data, conditions):
                            # Tạo đường dẫn file ảnh
                            file_path = self._get_image_path(img_data)
                            
                            # Thêm thông tin ảnh
                            image_info = {
                                'image_index': img_data.get('image_index', 0),
                                'series_description': img_data.get('SeriesDescription', ''),
                                'modality': img_data.get('Modality', ''),
                                'manufacturer': img_data.get('Manufacturer', ''),
                                'patient_age': img_data.get('PatientAge', ''),
                                'patient_sex': img_data.get('PatientSex', ''),
                                'slice_thickness': img_data.get('SliceThickness', ''),
                                'magnetic_field_strength': img_data.get('MagneticFieldStrength', ''),
                                'file_path': file_path,
                                'file_exists': os.path.exists(file_path) if file_path else False
                            }
                            
                            matching_images.append(image_info)
                            
                except Exception as e:
                    print(f"Lỗi xử lý metadata {key}: {e}")
                    continue
            
            result['matching_images'] = matching_images
            result['total_matching_images'] = len(matching_images)
            result['total_patient_images'] = len(all_images)
            result['match_percentage'] = (len(matching_images) / len(all_images)) * 100 if all_images else 0
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'patient_id': patient_id,
                'conditions': conditions,
                'error': str(e),
                'clinical_notes': '',
                'matching_images': [],
                'total_matching_images': 0,
                'total_patient_images': 0,
                'match_percentage': 0.0
            }
    
    def _matches_conditions(self, img_data: Dict, conditions: Dict[str, str]) -> bool:
        """Kiểm tra xem ảnh có phù hợp với điều kiện không"""
        for field, value in conditions.items():
            # Map field names to actual metadata fields
            field_mapping = {
                'series_description': 'SeriesDescription',
                'modality': 'Modality', 
                'manufacturer': 'Manufacturer',
                'patient_sex': 'PatientSex',
                'patient_age': 'PatientAge'
            }
            
            actual_field = field_mapping.get(field, field)
            
            if actual_field not in img_data:
                return False
            
            # Case-insensitive partial matching
            img_value = str(img_data[actual_field]).lower()
            search_value = str(value).lower()
            
            if search_value not in img_value:
                return False
        
        return True
    
    def _get_image_path(self, img_data: Dict) -> str:
        """Tạo đường dẫn file ảnh từ metadata"""
        try:
            patient_id = img_data.get('patient_id', '')
            series_desc = img_data.get('SeriesDescription', '')
            image_index = img_data.get('image_index', 0)
            
            if patient_id and series_desc:
                base_path = f"{self.image_base_path}/{patient_id.zfill(4)}"
                
                if os.path.exists(base_path):
                    for subdir in os.listdir(base_path):
                        if subdir.startswith("L-SPINE_LSS_"):
                            # Tìm thư mục series phù hợp
                            series_dirs = [d for d in os.listdir(os.path.join(base_path, subdir)) 
                                         if series_desc.replace(' ', '_').upper() in d.upper()]
                            if series_dirs:
                                series_path = os.path.join(base_path, subdir, series_dirs[0])
                                if os.path.exists(series_path):
                                    # Tìm file thực tế trong thư mục
                                    files = os.listdir(series_path)
                                    # Tìm file có pattern phù hợp
                                    for f in files:
                                        if f.endswith('.ima') and patient_id.zfill(4) in f:
                                            return os.path.join(series_path, f).replace('\\', '/')
            
            return ""
        except:
            return ""

def main():
    """Demo function"""
    print("🔍 NGHIÊN CỨU TÌNH HUỐNG 2: Bệnh nhân + Điều kiện")
    print("=" * 50)
    
    try:
        api = Case2API()
        
        # Test connection
        api.client.ping()
        print("✅ Đã kết nối Redis")
        
        # Get available patients
        patient_keys = api.client.keys("patient:*")
        available_patients = [key.decode().split(':')[1] for key in patient_keys]
        print(f"📊 Số bệnh nhân có sẵn: {len(available_patients)}")
        print(f"📋 VD: {', '.join(available_patients[:10])}")
        
        if not available_patients:
            print("❌ Không tìm thấy bệnh nhân!")
            return
        
        # Demo với patient đầu tiên
        patient_id = available_patients[0]
        print(f"\n🔍 Đang thử nghiệm với bệnh nhân: {patient_id}")
        
        # Demo các điều kiện khác nhau
        test_conditions = [
            {"series_description": "t2"},
            {"modality": "MR"},
            {"series_description": "sagittal"},
            {"series_description": "t2", "modality": "MR"}
        ]
        
        for i, conditions in enumerate(test_conditions, 1):
            print(f"\n📋 Thử nghiệm {i}: Điều kiện = {conditions}")
            result = api.get_patient_with_conditions(patient_id, conditions)
            
            if result['success']:
                print(f"✅ Tìm thấy {result['total_matching_images']} ảnh phù hợp")
                print(f"📊 Tỷ lệ khớp: {result['match_percentage']:.1f}%")
                
                if result['matching_images']:
                    print(f"📋 Ảnh khớp mẫu:")
                    for j, img in enumerate(result['matching_images'][:2]):
                        print(f"   {j+1}. {img['series_description']} ({img['modality']})")
            else:
                print(f"❌ Lỗi: {result['error']}")
        
        print(f"\n📖 Cách sử dụng API:")
        print(f"   Đầu vào: patient_id (chuỗi) + conditions (từ điển)")
        print(f"   Ví dụ: api.get_patient_with_conditions('70', {{'series_description': 't2'}})")
        print(f"   Trả về: clinical_notes + danh sách matching_images")
        
        print(f"\n🔧 Các trường điều kiện có sẵn:")
        print(f"   - series_description: 't2', 't1', 'sagittal', 'tra', 'localizer'")
        print(f"   - modality: 'MR'")
        print(f"   - manufacturer: 'SIEMENS', 'GE', 'PHILIPS'")
        print(f"   - patient_sex: 'M', 'F'")
        print(f"   - patient_age: '30Y', '40Y', v.v.")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
