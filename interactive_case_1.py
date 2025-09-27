#!/usr/bin/env python3
"""
Interactive Case Study 1: Truy xuất văn bản và ảnh khi biết patient ID
"""

from api_case_1 import Case1API
import json

def interactive_case_1():
    """Interactive interface cho Case Study 1"""
    print("🔍 NGHIÊN CỨU TÌNH HUỐNG 1: Tra cứu bệnh nhân cơ bản")
    print("=" * 50)
    
    try:
        api = Case1API()
        
        # Test connection
        api.client.ping()
        print("✅ Đã kết nối Redis")
        
        # Lấy danh sách patients có sẵn
        patient_keys = api.client.keys("patient:*")
        available_patients = [key.decode().split(':')[1] for key in patient_keys]
        print(f"📊 Số bệnh nhân có sẵn: {len(available_patients)}")
        
        if not available_patients:
            print("❌ Không tìm thấy bệnh nhân!")
            return
        
        print(f"📋 VD: {', '.join(available_patients[:10])}")
        
        while True:
            print(f"\n{'='*50}")
            print("🔍 NGHIÊN CỨU TÌNH HUỐNG 1: Tra cứu bệnh nhân cơ bản")
            print("=" * 50)
            
            # Nhập patient ID
            patient_id = input(f"\n📝 Nhập ID bệnh nhân (hoặc 'quit' để thoát): ").strip()
            
            if patient_id.lower() == 'quit':
                print("👋 Tạm biệt!")
                break
            
            if not patient_id:
                print("❌ Vui lòng nhập ID bệnh nhân hợp lệ")
                continue
            
            # Kiểm tra patient có tồn tại không
            if patient_id not in available_patients:
                print(f"❌ Không tìm thấy bệnh nhân {patient_id}!")
                print(f"💡 VD: {', '.join(available_patients[:10])}...")
                continue
            
            print(f"\n🔍 Đang tìm kiếm bệnh nhân {patient_id}...")
            
            # Gọi API
            result = api.get_patient_data(patient_id)
            
            if result['success']:
                print(f"\n✅ Tìm thấy bệnh nhân {patient_id}!")
                print(f"📝 Ghi chú lâm sàng:")
                print(f"   {result['clinical_notes']}")
                print(f"\n🖼️  Tổng số ảnh: {result['total_images']}")
                
                if result['mri_images']:
                    print(f"\n📋 Ảnh MRI:")
                    for i, img in enumerate(result['mri_images'][:10]):  # Hiển thị 10 ảnh đầu
                        print(f"   {i+1:2d}. {img['series_description']:<25} ({img['modality']})")
                        print(f"       Tuổi: {img['patient_age']}, Giới tính: {img['patient_sex']}")
                        print(f"       File tồn tại: {img['file_exists']}")
                        print()
                    
                    if len(result['mri_images']) > 10:
                        print(f"   ... và {len(result['mri_images']) - 10} ảnh khác")
                
                # Tùy chọn xem chi tiết
                choice = input(f"\n🔍 Bạn có muốn xem thông tin chi tiết của một ảnh cụ thể không? (y/n): ").strip().lower()
                if choice == 'y':
                    while True:
                        try:
                            img_input = input(f"Có {len(result['mri_images'])} ảnh bạn muốn xem chi tiết ảnh thứ (hoặc 'quit' để thoát): ").strip()
                            
                            if img_input.lower() == 'quit':
                                print("👋 Thoát xem chi tiết ảnh")
                                break
                            
                            img_index = int(img_input)
                            if 1 <= img_index <= len(result['mri_images']):
                                actual_index = img_index - 1  # Chuyển đổi từ 1-based sang 0-based
                                img = result['mri_images'][actual_index]
                                print(f"\n📋 Thông tin chi tiết cho ảnh {img_index}:")
                                print(f"   Mô tả series: {img['series_description']}")
                                print(f"   Phương thức: {img['modality']}")
                                print(f"   Nhà sản xuất: {img['manufacturer']}")
                                print(f"   Tuổi bệnh nhân: {img['patient_age']}")
                                print(f"   Giới tính bệnh nhân: {img['patient_sex']}")
                                print(f"   Độ dày lát cắt: {img['slice_thickness']}")
                                print(f"   Cường độ từ trường: {img['magnetic_field_strength']}")
                                print(f"   Đường dẫn file: {img['file_path']}")
                                print(f"   File tồn tại: {img['file_exists']}")
                                
                                # Hỏi có muốn xem ảnh khác không
                                continue_choice = input(f"\n🔄 Bạn có muốn xem ảnh khác không? (y/n): ").strip().lower()
                                if continue_choice != 'y':
                                    break
                            else:
                                print(f"❌ Chỉ số ảnh phải từ 1 đến {len(result['mri_images'])}!")
                        except ValueError:
                            print("❌ Vui lòng nhập số hợp lệ hoặc 'quit'!")
            else:
                print(f"❌ Lỗi: {result['error']}")
            
            # Tùy chọn tiếp tục
            continue_choice = input(f"\n🔄 Bạn có muốn tìm kiếm bệnh nhân khác không? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("👋 Tạm biệt!")
                break
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    interactive_case_1()

