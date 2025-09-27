#!/usr/bin/env python3
"""
API Case Study 3: Truy xuất ảnh MRI tương tự với một ảnh MRI đã cho
"""

import redis
import json
import os
from typing import Dict, Any, List

class Case3API:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)
        self.image_base_path = "data/image_data/01_MRI_Data"
    
    def find_similar_images(self, reference_patient_id: str, reference_image_index: int, top_n: int = 10) -> Dict[str, Any]:
        """
        Truy xuất ảnh MRI tương tự với một ảnh MRI đã cho
        
        Args:
            reference_patient_id (str): ID của bệnh nhân tham chiếu (ví dụ: "70")
            reference_image_index (int): Index của ảnh tham chiếu (ví dụ: 0, 1, 2...)
            top_n (int): Số lượng ảnh tương tự tối đa trả về (mặc định: 10)
        
        Returns:
            Dict chứa ảnh tham chiếu và danh sách ảnh tương tự
        """
        try:
            result = {
                'success': True,
                'reference_image': {},
                'similar_images': [],
                'total_similar': 0,
                'error': None
            }
            
            # 1. Lấy ảnh tham chiếu
            ref_image = self._get_reference_image(reference_patient_id, reference_image_index)
            
            if not ref_image:
                result['success'] = False
                result['error'] = f"Reference image not found for patient {reference_patient_id} at index {reference_image_index}"
                return result
            
            result['reference_image'] = ref_image
            
            # 2. Tìm ảnh tương tự
            similar_images = self._find_similar_images(ref_image, reference_patient_id, top_n)
            result['similar_images'] = similar_images
            result['total_similar'] = len(similar_images)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'reference_image': {},
                'similar_images': [],
                'total_similar': 0,
                'error': str(e)
            }
    
    def _get_reference_image(self, patient_id: str, image_index: int) -> Dict[str, Any]:
        """Lấy ảnh tham chiếu"""
        try:
            pattern = f"metadata:{patient_id}:*"
            keys = self.client.keys(pattern)
            
            if not keys or image_index >= len(keys):
                return None
            
            # Lấy ảnh theo index
            key = keys[image_index]
            metadata = self.client.get(key)
            
            if not metadata:
                return None
            
            img_data = json.loads(metadata)
            
            # Tạo đường dẫn file ảnh
            file_path = self._get_image_path(img_data)
            
            return {
                'patient_id': patient_id,
                'image_index': image_index,
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
            
        except Exception as e:
            print(f"Lỗi lấy ảnh tham chiếu: {e}")
            return None
    
    def _find_similar_images(self, ref_image: Dict, ref_patient_id: str, top_n: int) -> List[Dict[str, Any]]:
        """Tìm ảnh tương tự"""
        try:
            # Lấy tất cả metadata từ tất cả patients
            all_metadata = self._get_all_metadata()
            similarities = []
            
            # Các trường để so sánh
            comparison_fields = [
                'SeriesDescription', 'Modality', 'Manufacturer', 
                'SliceThickness', 'MagneticFieldStrength'
            ]
            
            for img_data in all_metadata:
                # Bỏ qua ảnh của cùng patient
                if str(img_data.get('patient_id', '')) == str(ref_patient_id):
                    continue
                
                # Tính điểm tương tự
                similarity_score = self._calculate_similarity(ref_image, img_data, comparison_fields)
                
                if similarity_score > 0.0:  # Lấy tất cả ảnh có độ tương tự > 0%
                    # Tạo đường dẫn file ảnh
                    file_path = self._get_image_path(img_data)
                    
                    similar_img = {
                        'patient_id': img_data.get('patient_id', ''),
                        'image_index': img_data.get('image_index', 0),
                        'series_description': img_data.get('SeriesDescription', ''),
                        'modality': img_data.get('Modality', ''),
                        'manufacturer': img_data.get('Manufacturer', ''),
                        'patient_age': img_data.get('PatientAge', ''),
                        'patient_sex': img_data.get('PatientSex', ''),
                        'slice_thickness': img_data.get('SliceThickness', ''),
                        'magnetic_field_strength': img_data.get('MagneticFieldStrength', ''),
                        'similarity_score': similarity_score,
                        'file_path': file_path,
                        'file_exists': os.path.exists(file_path) if file_path else False
                    }
                    
                    similarities.append(similar_img)
            
            # Sắp xếp theo điểm tương tự
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similarities[:top_n]
            
        except Exception as e:
            print(f"Lỗi tìm ảnh tương tự: {e}")
            return []
    
    def _calculate_similarity(self, ref_image: Dict, img_data: Dict, comparison_fields: List[str]) -> float:
        """Tính điểm tương tự giữa 2 ảnh"""
        try:
            score = 0
            total_fields = 0
            
            for field in comparison_fields:
                # Map field names từ ref_image format sang img_data format
                ref_field = field
                if field == 'SeriesDescription':
                    ref_field = 'series_description'
                elif field == 'Modality':
                    ref_field = 'modality'
                elif field == 'Manufacturer':
                    ref_field = 'manufacturer'
                elif field == 'SliceThickness':
                    ref_field = 'slice_thickness'
                elif field == 'MagneticFieldStrength':
                    ref_field = 'magnetic_field_strength'
                
                ref_value = ref_image.get(ref_field, '')
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
            
        except Exception as e:
            print(f"Lỗi tính toán độ tương tự: {e}")
            return 0
    
    def _get_all_metadata(self) -> List[Dict]:
        """Lấy tất cả metadata từ Redis"""
        try:
            all_keys = self.client.keys("metadata:*:*")
            all_data = []
            
            for key in all_keys:
                try:
                    result = self.client.get(key)
                    if result:
                        all_data.append(json.loads(result))
                except Exception as e:
                    print(f"Lỗi đọc {key}: {e}")
                    continue
            
            return all_data
        except Exception as e:
            print(f"Lỗi lấy tất cả metadata: {e}")
            return []
    
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
    print("🔍 NGHIÊN CỨU TÌNH HUỐNG 3: Ảnh tương tự")
    print("=" * 50)
    
    try:
        api = Case3API()
        
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
        image_index = 0
        top_n = 5
        
        print(f"\n🔍 Đang thử nghiệm với bệnh nhân: {patient_id}, chỉ số ảnh: {image_index}")
        
        result = api.find_similar_images(patient_id, image_index, top_n)
        
        if result['success']:
            print(f"✅ Tìm thấy {result['total_similar']} ảnh tương tự")
            print(f"🔍 Ảnh tham chiếu: {result['reference_image']['series_description']}")
            
            if result['similar_images']:
                print(f"📋 Ảnh tương tự hàng đầu:")
                for i, img in enumerate(result['similar_images'][:3]):
                    print(f"   {i+1}. Bệnh nhân {img['patient_id']}: {img['series_description']}")
                    print(f"      Độ tương tự: {img['similarity_score']:.2f} ({img['modality']})")
        else:
            print(f"❌ Lỗi: {result['error']}")
        
        print(f"\n📖 Cách sử dụng API:")
        print(f"   Đầu vào: reference_patient_id (chuỗi) + reference_image_index (số nguyên) + top_n (số nguyên)")
        print(f"   Ví dụ: api.find_similar_images('70', 0, 5)")
        print(f"   Trả về: reference_image + danh sách similar_images")
        
        print(f"\n🔧 Tiêu chí tương tự:")
        print(f"   - SeriesDescription (khớp chính xác + khớp một phần)")
        print(f"   - Modality (khớp chính xác)")
        print(f"   - Manufacturer (khớp chính xác)")
        print(f"   - SliceThickness (khớp chính xác)")
        print(f"   - MagneticFieldStrength (khớp chính xác)")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
