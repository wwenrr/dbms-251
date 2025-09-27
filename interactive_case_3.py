#!/usr/bin/env python3
"""
Interactive Case Study 3: Truy xuất ảnh MRI tương tự với một ảnh MRI đã cho
"""

from api_case_3 import Case3API
import json

def interactive_case_3():
    """Interactive interface cho Case Study 3"""
    print("🔍 NGHIÊN CỨU TÌNH HUỐNG 3: Ảnh tương tự")
    print("=" * 50)
    
    try:
        api = Case3API()
        
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
            print("🔍 NGHIÊN CỨU TÌNH HUỐNG 3: Ảnh tương tự")
            print("=" * 50)
            
            # Nhập patient ID
            patient_id = input(f"\n📝 Nhập ID bệnh nhân tham chiếu (hoặc 'quit' để thoát): ").strip()
            
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
            
            # Lấy số lượng ảnh của patient
            pattern = f"metadata:{patient_id}:*"
            keys = api.client.keys(pattern)
            total_images = len(keys)
            
            if total_images == 0:
                print(f"❌ Bệnh nhân {patient_id} không có ảnh!")
                continue
            
            print(f"📊 Bệnh nhân {patient_id} có {total_images} ảnh")
            
            # Nhập image index
            try:
                image_index = int(input(f"Có {total_images} ảnh bạn muốn xem chi tiết ảnh thứ: "))
                if not (1 <= image_index <= total_images):
                    print(f"❌ Chỉ số ảnh phải nằm trong khoảng 1 đến {total_images}")
                    continue
                actual_image_index = image_index - 1  # Chuyển đổi từ 1-based sang 0-based
            except ValueError:
                print("❌ Vui lòng nhập số hợp lệ!")
                continue
            
            # Nhập số lượng ảnh tương tự
            try:
                top_n = int(input(f"Nhập số lượng ảnh tương tự cần tìm (mặc định 5): ") or "5")
                if top_n <= 0:
                    print("❌ Số phải dương!")
                    continue
            except ValueError:
                print("❌ Vui lòng nhập số hợp lệ!")
                continue
            
            print(f"\n🔍 Đang tìm ảnh tương tự cho bệnh nhân {patient_id}, ảnh {image_index}...")
            
            # Gọi API
            result = api.find_similar_images(patient_id, actual_image_index, top_n)
            
            if result['success']:
                print(f"\n✅ Tìm kiếm hoàn tất!")
                print(f"🔍 Ảnh tham chiếu:")
                ref_img = result['reference_image']
                print(f"   ID bệnh nhân: {ref_img['patient_id']}")
                print(f"   Chỉ số ảnh: {ref_img['image_index']}")
                print(f"   Mô tả series: {ref_img['series_description']}")
                print(f"   Phương thức: {ref_img['modality']}")
                print(f"   Nhà sản xuất: {ref_img['manufacturer']}")
                print(f"   Tuổi bệnh nhân: {ref_img['patient_age']}")
                print(f"   Giới tính bệnh nhân: {ref_img['patient_sex']}")
                print(f"   File tồn tại: {ref_img['file_exists']}")
                
                print(f"\n📊 Kết quả:")
                print(f"   Tổng số ảnh tương tự tìm thấy: {result['total_similar']}")
                
                if result['similar_images']:
                    print(f"\n📋 Ảnh tương tự:")
                    for i, img in enumerate(result['similar_images']):
                        print(f"   {i+1:2d}. Bệnh nhân {img['patient_id']}: {img['series_description']}")
                        print(f"       Độ tương tự: {img['similarity_score']:.2f} ({img['modality']})")
                        print(f"       Tuổi: {img['patient_age']}, Giới tính: {img['patient_sex']}")
                        print(f"       Nhà sản xuất: {img['manufacturer']}")
                        print(f"       File tồn tại: {img['file_exists']}")
                        print()
                    
                    # Tùy chọn xem chi tiết
                    choice = input(f"\n🔍 Bạn có muốn xem thông tin chi tiết của một ảnh tương tự cụ thể không? (y/n): ").strip().lower()
                    if choice == 'y':
                        while True:
                            try:
                                img_input = input(f"Có {len(result['similar_images'])} ảnh tương tự bạn muốn xem chi tiết ảnh thứ (hoặc 'quit' để thoát): ").strip()
                                
                                if img_input.lower() == 'quit':
                                    print("👋 Thoát xem chi tiết ảnh")
                                    break
                                
                                img_index = int(img_input)
                                if 1 <= img_index <= len(result['similar_images']):
                                    actual_index = img_index - 1  # Chuyển đổi từ 1-based sang 0-based
                                    img = result['similar_images'][actual_index]
                                    print(f"\n📋 Thông tin chi tiết cho ảnh tương tự {img_index}:")
                                    print(f"   ID bệnh nhân: {img['patient_id']}")
                                    print(f"   Chỉ số ảnh: {img['image_index']}")
                                    print(f"   Mô tả series: {img['series_description']}")
                                    print(f"   Phương thức: {img['modality']}")
                                    print(f"   Nhà sản xuất: {img['manufacturer']}")
                                    print(f"   Tuổi bệnh nhân: {img['patient_age']}")
                                    print(f"   Giới tính bệnh nhân: {img['patient_sex']}")
                                    print(f"   Độ dày lát cắt: {img['slice_thickness']}")
                                    print(f"   Cường độ từ trường: {img['magnetic_field_strength']}")
                                    print(f"   Điểm tương tự: {img['similarity_score']:.2f}")
                                    print(f"   Đường dẫn file: {img['file_path']}")
                                    print(f"   File tồn tại: {img['file_exists']}")
                                    
                                    # Hỏi có muốn xem ảnh khác không
                                    continue_choice = input(f"\n🔄 Bạn có muốn xem ảnh tương tự khác không? (y/n): ").strip().lower()
                                    if continue_choice != 'y':
                                        break
                                else:
                                    print(f"❌ Chỉ số ảnh phải từ 1 đến {len(result['similar_images'])}!")
                            except ValueError:
                                print("❌ Vui lòng nhập số hợp lệ hoặc 'quit'!")
                else:
                    print(f"\n❌ Không tìm thấy ảnh tương tự!")
            else:
                print(f"❌ Lỗi: {result['error']}")
            
            # Tùy chọn tiếp tục
            continue_choice = input(f"\n🔄 Bạn có muốn tìm kiếm ảnh tham chiếu khác không? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("👋 Tạm biệt!")
                break
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    interactive_case_3()

