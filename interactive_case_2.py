#!/usr/bin/env python3
"""
Interactive Case Study 2: Truy xuất văn bản và ảnh khi biết patient ID + điều kiện cụ thể
"""

from api_case_2 import Case2API
import json

def interactive_case_2():
    """Interactive interface cho Case Study 2"""
    print("🔍 NGHIÊN CỨU TÌNH HUỐNG 2: Bệnh nhân + Điều kiện")
    print("=" * 50)
    
    try:
        api = Case2API()
        
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
            print("🔍 NGHIÊN CỨU TÌNH HUỐNG 2: Bệnh nhân + Điều kiện")
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
            
            # Hiển thị các điều kiện có thể sử dụng
            print(f"\n🔧 Các trường điều kiện có sẵn:")
            print(f"   - series_description: 't2', 't1', 'sagittal', 'tra', 'localizer'")
            print(f"   - modality: 'MR'")
            print(f"   - manufacturer: 'SIEMENS', 'GE', 'PHILIPS'")
            print(f"   - patient_sex: 'M', 'F'")
            print(f"   - patient_age: '30Y', '40Y', v.v.")
            
            # Nhập điều kiện
            print(f"\n📝 Nhập điều kiện tìm kiếm:")
            conditions = {}
            
            # Series description
            series_desc = input(f"   Mô tả series (tùy chọn, ví dụ: 't2', 't1', 'sagittal'): ").strip()
            if series_desc:
                conditions['series_description'] = series_desc
            
            # Modality
            modality = input(f"   Phương thức (tùy chọn, ví dụ: 'MR'): ").strip()
            if modality:
                conditions['modality'] = modality
            
            # Manufacturer
            manufacturer = input(f"   Nhà sản xuất (tùy chọn, ví dụ: 'SIEMENS', 'GE'): ").strip()
            if manufacturer:
                conditions['manufacturer'] = manufacturer
            
            # Patient sex
            patient_sex = input(f"   Giới tính bệnh nhân (tùy chọn, 'M' hoặc 'F'): ").strip()
            if patient_sex:
                conditions['patient_sex'] = patient_sex
            
            # Patient age
            patient_age = input(f"   Tuổi bệnh nhân (tùy chọn, ví dụ: '30Y', '40Y'): ").strip()
            if patient_age:
                conditions['patient_age'] = patient_age
            
            if not conditions:
                print("❌ Vui lòng nhập ít nhất một điều kiện!")
                continue
            
            print(f"\n🔍 Đang tìm kiếm bệnh nhân {patient_id} với điều kiện: {conditions}")
            
            # Gọi API
            result = api.get_patient_with_conditions(patient_id, conditions)
            
            if result['success']:
                print(f"\n✅ Tìm kiếm hoàn tất!")
                print(f"📝 Ghi chú lâm sàng:")
                print(f"   {result['clinical_notes']}")
                print(f"\n📊 Kết quả:")
                print(f"   Tổng ảnh bệnh nhân: {result['total_patient_images']}")
                print(f"   Ảnh khớp: {result['total_matching_images']}")
                print(f"   Tỷ lệ khớp: {result['match_percentage']:.1f}%")
                
                if result['matching_images']:
                    print(f"\n📋 Ảnh khớp:")
                    for i, img in enumerate(result['matching_images'][:10]):  # Hiển thị 10 ảnh đầu
                        print(f"   {i+1:2d}. {img['series_description']:<25} ({img['modality']})")
                        print(f"       Tuổi: {img['patient_age']}, Giới tính: {img['patient_sex']}")
                        print(f"       Nhà sản xuất: {img['manufacturer']}")
                        print(f"       File tồn tại: {img['file_exists']}")
                        print()
                    
                    if len(result['matching_images']) > 10:
                        print(f"   ... và {len(result['matching_images']) - 10} ảnh khác")
                else:
                    print(f"\n❌ Không tìm thấy ảnh nào khớp với điều kiện!")
                
                # Tùy chọn xem chi tiết
                if result['matching_images']:
                    choice = input(f"\n🔍 Bạn có muốn xem thông tin chi tiết của một ảnh cụ thể không? (y/n): ").strip().lower()
                    if choice == 'y':
                        while True:
                            try:
                                img_input = input(f"Có {len(result['matching_images'])} ảnh bạn muốn xem chi tiết ảnh thứ (hoặc 'quit' để thoát): ").strip()
                                
                                if img_input.lower() == 'quit':
                                    print("👋 Thoát xem chi tiết ảnh")
                                    break
                                
                                img_index = int(img_input)
                                if 1 <= img_index <= len(result['matching_images']):
                                    actual_index = img_index - 1  # Chuyển đổi từ 1-based sang 0-based
                                    img = result['matching_images'][actual_index]
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
                                    print(f"❌ Chỉ số ảnh phải từ 1 đến {len(result['matching_images'])}!")
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
    interactive_case_2()

