import pandas as pd
from collections import Counter # Thư viện để đếm tần suất
import re

print("--- KHỞI ĐỘNG HỆ THỐNG PHÂN TÍCH LỖ HỔNG (v2 - CÓ LỌC) ---")

# --- BƯỚC 1: ĐỊNH NGHĨA CÁC DANH MỤC KỸ NĂNG ---
from skills_config import HARD_SKILLS, SOFT_BUSINESS_SKILLS

# --- BƯỚC 2: HÀM TẢI KỸ NĂNG CỦA SINH VIÊN (như cũ) ---
def load_student_skills(csv_file):
    try:
        df = pd.read_csv(csv_file)
        student_skills = set(df['Extracted_Skill'].str.lower().unique())
        print(f"\n[SINH VIÊN] Đã tải {len(student_skills)} kỹ năng của sinh viên.")
        return student_skills
    except FileNotFoundError:
        print(f"[LỖI] Không tìm thấy file kỹ năng sinh viên: {csv_file}")
        return set()

# --- BƯỚC 3: HÀM PHÂN TÍCH KỸ NĂNG THỊ TRƯỜNG (như cũ) ---
def analyze_market_skills(csv_file, search_keyword):
    try:
        df = pd.read_csv(csv_file)
        keyword = search_keyword.lower()
        df_filtered = df[df['Job_Title'].str.lower().str.contains(keyword, na=False)]
        
        num_jobs = len(df_filtered)
        if num_jobs == 0:
            print(f"\n[THỊ TRƯỜNG] Không tìm thấy công việc nào khớp với từ khóa: '{keyword}'")
            return None, None

        print(f"\n[THỊ TRƯỜNG] Đã tìm thấy {num_jobs} công việc cho từ khóa '{keyword}'.")
        
        all_skills_list = []
        for skills_str in df_filtered['Skills_Found'].dropna():
            skills = [skill.strip().lower() for skill in skills_str.split(',')]
            all_skills_list.extend(skills)
            
        skill_counts = Counter(all_skills_list)
        
        # Lấy ra 20 kỹ năng phổ biến nhất (thay vì 10)
        top_20_skills = skill_counts.most_common(20)
        
        print(f"--- Top 20 Kỹ năng Thị trường Yêu cầu (cho '{keyword}') ---")
        market_profile_set = set()
        for skill, count in top_20_skills:
            if skill.strip() == "": continue
            percentage = (count / num_jobs) * 100
            print(f"  {skill}: {percentage:.1f}% (xuất hiện trong {count} tin)")
            market_profile_set.add(skill)
        
        return market_profile_set, skill_counts # Trả về cả danh sách Top và danh sách đếm

    except FileNotFoundError:
        print(f"[LỖI] Không tìm thấy file kỹ năng thị trường: {csv_file}")
        return None, None

# --- BƯỚC 4: CHẠY CHƯƠNG TRÌNH CHÍNH (ĐÃ NÂNG CẤP) ---
if __name__ == "__main__":
    
    # 1. Tải kỹ năng sinh viên
    student_skills_set = load_student_skills('extracted_skills.csv')
    
    if not student_skills_set:
        print("Không thể tiếp tục vì không có kỹ năng sinh viên.")
    else:
        # 2. Tải và Phân tích thị trường
        target_role = input("\nNhập vai trò bạn muốn so sánh (ví dụ: Backend, Frontend, Data): ")
        
        if target_role:
            market_profile, market_counts = analyze_market_skills('market_skills.csv', target_role)
            
            if market_profile:
                # --- PHẦN MỚI: HỎI NGƯỜI DÙNG LỌC ---
                print("\nBạn muốn lọc theo nhóm kỹ năng nào?")
                print("  1: Tất cả (mặc định)")
                print("  2: Chỉ Kỹ năng Cứng (Code, Tech, Tool)")
                print("  3: Chỉ Kỹ năng Mềm & Nghiệp vụ (Soft skills, Language, Business)")
                choice = input("Nhập lựa chọn (1, 2, hoặc 3): ")

                filtered_market_profile = market_profile.copy() # Bắt đầu với tất cả

                if choice == '2':
                    # Lọc: chỉ giữ lại những skill có trong HARD_SKILLS
                    filtered_market_profile = market_profile.intersection(HARD_SKILLS)
                    print("\n--- Đã lọc: Chỉ hiển thị Kỹ năng Cứng ---")
                elif choice == '3':
                    # Lọc: chỉ giữ lại những skill có trong SOFT_BUSINESS_SKILLS
                    filtered_market_profile = market_profile.intersection(SOFT_BUSINESS_SKILLS)
                    print("\n--- Đã lọc: Chỉ hiển thị Kỹ năng Mềm & Nghiệp vụ ---")
                else:
                    print("\n--- Hiển thị: Tất cả kỹ năng ---")

                # 3. Thực hiện Phân tích Lỗ hổng (trên danh sách đã lọc)
                print("\n--- KẾT QUẢ PHÂN TÍCH LỖ HỔNG ---")
                
                if not filtered_market_profile:
                    print("❌ Không có kỹ năng nào trong Top 20 khớp với bộ lọc của bạn.")
                else:
                    matching_skills = student_skills_set.intersection(filtered_market_profile)
                    missing_skills = filtered_market_profile.difference(student_skills_set)
                    
                    if matching_skills:
                        print(f"✅ Kỹ năng CHUẨN (Bạn đã có):")
                        print(f"  {', '.join(matching_skills)}")
                    else:
                        print("❌ Bạn chưa có kỹ năng nào trong nhóm này.")
                        
                    if missing_skills:
                        print(f"\n🔥 Kỹ năng LỖ HỔNG (Bạn cần học GẤP):")
                        print(f"  {', '.join(missing_skills)}")
                    else:
                        print("\n✨ XUẤT SẮC! Bạn đã có TẤT CẢ kỹ năng trong nhóm này.")