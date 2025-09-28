#!/usr/bin/env python3
"""
Interactive Menu cho 3 Case Studies
"""

import os
import sys

def show_menu():
    """Hiển thị menu chính"""
    print("🏥 HỆ THỐNG CƠ SỞ DỮ LIỆU MRI - NGHIÊN CỨU TÌNH HUỐNG")
    print("=" * 70)
    print("📋 Chọn nghiên cứu tình huống:")
    print("   1. 🔍 Tìm thông tin bệnh nhân khi biết ID")
    print("   2. 🔍 Tìm bệnh nhân với bộ lọc (giới tính, tuổi, thiết bị...)")
    print("   3. 🔍 Tìm ảnh MRI tương tự với ảnh tham chiếu")
    print("   4. 🎯 Demo tất cả API - Chạy thử tất cả các chức năng")
    print("   5. 🚪 Thoát")
    print("=" * 70)

def run_case_study_1():
    """Chạy Case Study 1"""
    print("\n🔍 Đang khởi động: Tìm kiếm bệnh nhân cơ bản...")
    print("   → Nhập Patient ID để xem thông tin và ảnh MRI")
    os.system("python interactive_case_1.py")

def run_case_study_2():
    """Chạy Case Study 2"""
    print("\n🔍 Đang khởi động: Tìm kiếm bệnh nhân có điều kiện...")
    print("   → Nhập Patient ID và các bộ lọc (giới tính, tuổi, thiết bị...)")
    os.system("python interactive_case_2.py")

def run_case_study_3():
    """Chạy Case Study 3"""
    print("\n🔍 Đang khởi động: Tìm ảnh tương tự...")
    print("   → Nhập Patient ID, Image Index và số lượng ảnh tương tự")
    os.system("python interactive_case_3.py")

def run_demo_all():
    """Chạy demo tất cả APIs"""
    print("\n🎯 Đang khởi động: Demo tất cả API...")
    print("   → Chạy thử tất cả các chức năng của hệ thống")
    os.system("python demo_all_apis.py")

def main():
    """Menu chính"""
    while True:
        try:
            show_menu()
            choice = input("\n📝 Nhập lựa chọn của bạn (1-5): ").strip()
            
            if choice == '1':
                run_case_study_1()
            elif choice == '2':
                run_case_study_2()
            elif choice == '3':
                run_case_study_3()
            elif choice == '4':
                run_demo_all()
            elif choice == '5':
                print("\n👋 Tạm biệt!")
                break
            else:
                print("\n❌ Lựa chọn không hợp lệ! Vui lòng nhập 1-5.")
            
            # Tạm dừng trước khi hiển thị menu lại
            if choice in ['1', '2', '3', '4']:
                input("\n⏸️  Nhấn Enter để tiếp tục...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            input("Nhấn Enter để tiếp tục...")

if __name__ == "__main__":
    main()

