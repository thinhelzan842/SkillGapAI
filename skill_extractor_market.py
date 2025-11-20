import pandas as pd

# Tải bộ não từ config
try:
    from skills_config import SKILL_MAPPING
    print("✅ Đã tải bộ não từ skills_config.py")
except ImportError:
    print("❌ Lỗi: Thiếu file skills_config.py")
    exit()

# --- HÀM TRÍCH XUẤT (Logic Mapping mới của bạn) ---
def extract_skills_from_text(jd_text, skill_mapping_dict):
    if not isinstance(jd_text, str): return ""
    
    found_skills = set()
    jd_lower = " " + jd_text.lower() + " "
    # Các ký tự phân cách
    separators = [' ', ',', '.', '/', '(', ')', '\n', ':', ';', '-', '!', '?', '"', "'", '[', ']']
    
    # Duyệt qua từng Kỹ năng CHUẨN
    for standard_skill, synonyms in skill_mapping_dict.items():
        is_found_skill = False
        for synonym in synonyms:
            synonym_lower = synonym.lower()
            if synonym_lower not in jd_lower: continue

            for sep_before in separators:
                for sep_after in separators:
                    if (sep_before + synonym_lower + sep_after) in jd_lower:
                        found_skills.add(standard_skill) # Lưu tên chuẩn
                        is_found_skill = True
                        break 
                if is_found_skill: break
            if is_found_skill: break
            
    return ", ".join(list(found_skills))

# --- HÀM CHẠY CHÍNH ---
def run_extraction():
    print("\n--- BẮT ĐẦU TRÍCH XUẤT KỸ NĂNG TỪ FILE THÔ ---")
    try:
        # 1. Đọc file thô vừa cào được
        df = pd.read_csv('raw_jobs.csv')
        print(f"📄 Đang đọc 'raw_jobs.csv' ({len(df)} công việc)...")
        
        # 2. Áp dụng hàm trích xuất
        print("🧠 Đang phân tích kỹ năng...")
        df['Skills_Found'] = df['JD_Text'].apply(lambda x: extract_skills_from_text(x, SKILL_MAPPING))
        
        # 3. Lưu file thành phẩm (để chạy gap_analysis.py)
        output_file = 'market_skills.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"✅ XONG! Kết quả đã lưu vào '{output_file}'.")
        print(f"👉 Bây giờ bạn có thể chạy 'gap_analysispy.py'.")

    except FileNotFoundError:
        print("❌ LỖI: Không tìm thấy file 'raw_jobs.csv'.")
        print("👉 Hãy chạy 'market_crawler.py' trước để lấy dữ liệu.")

if __name__ == "__main__":
    run_extraction()