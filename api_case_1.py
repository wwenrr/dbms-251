#!/usr/bin/env python3
"""
API Case Study 1: Truy xuất văn bản và ảnh khi biết patient ID
"""

import redis
import json
import os
from typing import Dict, Any, List

class Case1API:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)
        self.image_base_path = "data/image_data/01_MRI_Data"
    
    def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """
        Truy xuất văn bản và ảnh khi biết patient ID
        
        Args:
            patient_id (str): ID của bệnh nhân (ví dụ: "70", "1", "2")
            
        Returns:
            Dict chứa thông tin bệnh nhân, ghi chú lâm sàng và danh sách ảnh MRI
        """
        try:
            result = {
                'success': True,
                'patient_id': patient_id,
                'clinical_notes': '',
                'mri_images': [],
                'total_images': 0,
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
            
            for key in keys:
                try:
                    metadata = self.client.get(key)
                    if metadata:
                        img_data = json.loads(metadata)
                        
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
                        
                        result['mri_images'].append(image_info)
                        
                except Exception as e:
                    print(f"Lỗi xử lý metadata {key}: {e}")
                    continue
            
            result['total_images'] = len(result['mri_images'])
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'patient_id': patient_id,
                'error': str(e),
                'clinical_notes': '',
                'mri_images': [],
                'total_images': 0
            }
    
    def _get_image_path(self, img_data: Dict) -> str:
        """Tạo đường dẫn file ảnh từ metadata"""
        try:
            # Lấy thông tin từ metadata
            patient_id = img_data.get('patient_id', '')
            series_desc = img_data.get('SeriesDescription', '')
            image_index = img_data.get('image_index', 0)
            
            # Tạo đường dẫn
            if patient_id and series_desc:
                # Format: data/image_data/01_MRI_DATA/{patient_id}/L-SPINE_LSS_*/{series_desc}_*/{series_desc}_*_{patient_id}_{image_index:04d}.ima
                base_path = f"{self.image_base_path}/{patient_id.zfill(4)}"
                
                # Tìm thư mục con
                if os.path.exists(base_path):
                    for subdir in os.listdir(base_path):
                        if subdir.startswith("L-SPINE_LSS_"):
                            # Tìm thư mục series phù hợp
                            series_dirs = [d for d in os.listdir(os.path.join(base_path, subdir)) 
                                         if series_desc.replace(' ', '_').upper() in d.upper()]
                            if series_dirs:
                                series_path = os.path.join(base_path, subdir, series_dirs[0])
                                if os.path.exists(series_path):
                                    # Format file name theo cấu trúc thực tế
                                    # Tìm file thực tế trong thư mục
                                    if os.path.exists(series_path):
                                        files = os.listdir(series_path)
                                        # Tìm file có pattern phù hợp
                                        for f in files:
                                            if f.endswith('.ima') and patient_id.zfill(4) in f:
                                                return os.path.join(series_path, f).replace('\\', '/')
                                    return ""
            
            return ""
        except:
            return ""

def main():
    """Demo function"""
    print("🔍 NGHIÊN CỨU TÌNH HUỐNG 1: Tra cứu bệnh nhân cơ bản")
    print("=" * 50)
    
    try:
        api = Case1API()
        
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
        
        result = api.get_patient_data(patient_id)
        
        if result['success']:
            print(f"✅ Tìm thấy bệnh nhân {patient_id}")
            print(f"📝 Ghi chú lâm sàng: {result['clinical_notes'][:100]}...")
            print(f"🖼️  Tổng số ảnh: {result['total_images']}")
            
            if result['mri_images']:
                print(f"📋 Ảnh mẫu:")
                for i, img in enumerate(result['mri_images'][:3]):
                    print(f"   {i+1}. {img['series_description']} ({img['modality']})")
                    print(f"      File tồn tại: {img['file_exists']}")
        else:
            print(f"❌ Lỗi: {result['error']}")
        
        print(f"\n📖 Cách sử dụng API:")
        print(f"   Đầu vào: patient_id (chuỗi)")
        print(f"   Ví dụ: api.get_patient_data('70')")
        print(f"   Trả về: clinical_notes + danh sách mri_images")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()

