#!/usr/bin/env python3
"""
Demo tất cả 3 API Case Studies
"""

from api_case_1 import Case1API
from api_case_2 import Case2API
from api_case_3 import Case3API
import json

def demo_all_apis():
    """Demo tất cả 3 API"""
    print("🏥 CƠ SỞ DỮ LIỆU MRI - DEMO 3 NGHIÊN CỨU TÌNH HUỐNG")
    print("=" * 60)
    
    try:
        # Test connection
        api1 = Case1API()
        api1.client.ping()
        print("✅ Đã kết nối Redis")
        
        # Get available patients
        patient_keys = api1.client.keys("patient:*")
        available_patients = [key.decode().split(':')[1] for key in patient_keys]
        print(f"📊 Số bệnh nhân có sẵn: {len(available_patients)}")
        print(f"📋 VD: {', '.join(available_patients[:10])}")
        
        if not available_patients:
            print("❌ Không tìm thấy bệnh nhân!")
            return
        
        # Chọn patient để demo
        patient_id = available_patients[0]
        print(f"\n🎯 Demo với bệnh nhân: {patient_id}")
        
        # ========== CASE STUDY 1 ==========
        print(f"\n{'='*20} NGHIÊN CỨU TÌNH HUỐNG 1 {'='*20}")
        print("📋 Truy xuất văn bản và ảnh khi biết patient ID")
        print("-" * 50)
        
        api1 = Case1API()
        result1 = api1.get_patient_data(patient_id)
        
        if result1['success']:
            print(f"✅ Tìm thấy bệnh nhân {patient_id}")
            print(f"📝 Ghi chú lâm sàng: {result1['clinical_notes'][:100]}...")
            print(f"🖼️  Tổng số ảnh: {result1['total_images']}")
            
            if result1['mri_images']:
                print(f"📋 Ảnh mẫu:")
                for i, img in enumerate(result1['mri_images'][:3]):
                    print(f"   {i+1}. {img['series_description']} ({img['modality']})")
        else:
            print(f"❌ Lỗi: {result1['error']}")
        
        # ========== CASE STUDY 2 ==========
        print(f"\n{'='*20} NGHIÊN CỨU TÌNH HUỐNG 2 {'='*20}")
        print("📋 Truy xuất văn bản và ảnh khi biết patient ID + điều kiện cụ thể")
        print("-" * 50)
        
        api2 = Case2API()
        
        # Test các điều kiện khác nhau
        test_conditions = [
            {"series_description": "t2"},
            {"modality": "MR"},
            {"series_description": "sagittal"}
        ]
        
        for i, conditions in enumerate(test_conditions, 1):
            print(f"\n🔍 Thử nghiệm {i}: Điều kiện = {conditions}")
            result2 = api2.get_patient_with_conditions(patient_id, conditions)
            
            if result2['success']:
                print(f"✅ Tìm thấy {result2['total_matching_images']} ảnh khớp")
                print(f"📊 Tỷ lệ khớp: {result2['match_percentage']:.1f}%")
                
                if result2['matching_images']:
                    print(f"📋 Ảnh khớp mẫu:")
                    for j, img in enumerate(result2['matching_images'][:2]):
                        print(f"   {j+1}. {img['series_description']} ({img['modality']})")
            else:
                print(f"❌ Lỗi: {result2['error']}")
        
        # ========== CASE STUDY 3 ==========
        print(f"\n{'='*20} NGHIÊN CỨU TÌNH HUỐNG 3 {'='*20}")
        print("📋 Truy xuất ảnh MRI tương tự với một ảnh MRI đã cho")
        print("-" * 50)
        
        api3 = Case3API()
        image_index = 0
        top_n = 5
        
        print(f"🔍 Đang tìm ảnh tương tự cho bệnh nhân {patient_id}, chỉ số ảnh {image_index}")
        result3 = api3.find_similar_images(patient_id, image_index, top_n)
        
        if result3['success']:
            print(f"✅ Tìm thấy {result3['total_similar']} ảnh tương tự")
            print(f"🔍 Ảnh tham chiếu: {result3['reference_image']['series_description']}")
            
            if result3['similar_images']:
                print(f"📋 Ảnh tương tự hàng đầu:")
                for i, img in enumerate(result3['similar_images'][:3]):
                    print(f"   {i+1}. Bệnh nhân {img['patient_id']}: {img['series_description']}")
                    print(f"      Độ tương tự: {img['similarity_score']:.2f} ({img['modality']})")
        else:
            print(f"❌ Lỗi: {result3['error']}")
        
        # ========== API USAGE SUMMARY ==========
        print(f"\n{'='*20} TÓM TẮT CÁCH SỬ DỤNG API {'='*20}")
        print("📖 Cách sử dụng từng API:")
        print("-" * 50)
        
        print(f"\n🔧 NGHIÊN CỨU TÌNH HUỐNG 1 - Tra cứu bệnh nhân cơ bản:")
        print(f"   from api_case_1 import Case1API")
        print(f"   api = Case1API()")
        print(f"   result = api.get_patient_data('{patient_id}')")
        print(f"   # Đầu vào: patient_id (chuỗi)")
        print(f"   # Trả về: clinical_notes + danh sách mri_images")
        
        print(f"\n🔧 NGHIÊN CỨU TÌNH HUỐNG 2 - Bệnh nhân + Điều kiện:")
        print(f"   from api_case_2 import Case2API")
        print(f"   api = Case2API()")
        print(f"   result = api.get_patient_with_conditions('{patient_id}', {{'series_description': 't2'}})")
        print(f"   # Đầu vào: patient_id (chuỗi) + conditions (từ điển)")
        print(f"   # Trả về: clinical_notes + danh sách matching_images")
        
        print(f"\n🔧 NGHIÊN CỨU TÌNH HUỐNG 3 - Ảnh tương tự:")
        print(f"   from api_case_3 import Case3API")
        print(f"   api = Case3API()")
        print(f"   result = api.find_similar_images('{patient_id}', 0, 5)")
        print(f"   # Đầu vào: reference_patient_id (chuỗi) + reference_image_index (số nguyên) + top_n (số nguyên)")
        print(f"   # Trả về: reference_image + danh sách similar_images")
        
        print(f"\n✅ Tất cả API đã sẵn sàng sử dụng!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    demo_all_apis()

