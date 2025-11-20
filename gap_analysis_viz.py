import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Tải cấu hình bộ não
try:
    from skills_config import SKILL_MAPPING, HARD_SKILLS, SOFT_BUSINESS_SKILLS
except ImportError:
    print("❌ LỖI: Không tìm thấy file 'skills_config.py'.")
    exit()

print("--- KHỞI ĐỘNG HỆ THỐNG PHÂN TÍCH & TRỰC QUAN HÓA (v4.0 Pro Viz) ---")

# --- 1. HÀM TẢI DỮ LIỆU ---
def load_data():
    try:
        # Đọc file đã được làm sạch
        df_student = pd.read_csv('extracted_skills.csv')
        student_skills = set(df_student['Extracted_Skill'].str.lower().unique())
        
        df_market = pd.read_csv('market_skills.csv')
        
        print(f"✅ Đã tải: {len(student_skills)} kỹ năng sinh viên & {len(df_market)} tin tuyển dụng.")
        return student_skills, df_market
    except FileNotFoundError:
        print("❌ LỖI: Thiếu file CSV. Hãy chạy Script 1 và 2 trước.")
        return None, None

# --- 2. HÀM VẼ ROADMAP ĐẸP (NEW) ---
def draw_roadmap(ax, missing_skills, num_jobs):
    ax.axis('off')
    ax.set_title('ROADMAP: Lộ trình học kỹ năng còn thiếu\n(Ưu tiên từ trên xuống dưới)', 
                 fontweight='bold', fontsize=14, pad=20)

    if not missing_skills:
        ax.text(0.5, 0.5, "XUẤT SẮC! BẠN ĐÃ ĐỦ KỸ NĂNG!", 
                ha='center', va='center', fontsize=18, color='#2ecc71', fontweight='bold')
        return

    # Lấy Top 8 kỹ năng thiếu quan trọng nhất để vẽ cho đẹp (nhiều quá sẽ rối)
    top_missing = missing_skills[:8]
    n = len(top_missing)
    
    # Tọa độ vẽ
    start_y = 0.9
    gap_y = 0.11
    
    for i, (skill, count) in enumerate(top_missing):
        y_pos = start_y - (i * gap_y)
        importance = (count / num_jobs) * 100
        
        # 1. Vẽ hộp (Box)
        # Màu sắc đậm nhạt theo độ quan trọng
        alpha_val = 0.6 + (0.4 * (n - i) / n) 
        box_color = '#e67e22' # Màu cam
        
        # Vẽ hộp bo tròn
        rect = patches.FancyBboxPatch((0.1, y_pos - 0.04), 0.8, 0.08, 
                                      boxstyle="round,pad=0.02", 
                                      linewidth=1, edgecolor='none', facecolor=box_color, alpha=alpha_val)
        ax.add_patch(rect)
        
        # 2. Viết tên kỹ năng
        ax.text(0.15, y_pos, f"{i+1}. {skill.upper()}", 
                ha='left', va='center', fontsize=12, fontweight='bold', color='white')
        
        # 3. Viết độ quan trọng
        ax.text(0.85, y_pos, f"{importance:.1f}% Jobs", 
                ha='right', va='center', fontsize=10, color='white', style='italic')
        
        # 4. Vẽ mũi tên nối (trừ phần tử cuối)
        if i < n - 1:
            ax.arrow(0.5, y_pos - 0.04, 0, -0.03, 
                     head_width=0.02, head_length=0.02, fc='#7f8c8d', ec='#7f8c8d')

# --- 3. HÀM VẼ DASHBOARD ---
def visualize_results(target_role, market_stats, student_skills, num_jobs):
    # Tách dữ liệu
    skills = [item[0] for item in market_stats]
    counts = [item[1] for item in market_stats]
    percentages = [(c / num_jobs) * 100 for c in counts]
    
    # Phân loại kỹ năng
    colors = []
    matches = 0
    missing_data = [] # Lưu (skill, count) để vẽ roadmap
    
    for i, skill in enumerate(skills):
        if skill in student_skills:
            colors.append('#2ecc71') # Xanh (Có)
            matches += 1
        else:
            colors.append('#e74c3c') # Đỏ (Thiếu)
            missing_data.append((skill, counts[i]))
            
    # --- TẠO DASHBOARD ---
    fig = plt.figure(figsize=(16, 9), constrained_layout=True)
    gs = fig.add_gridspec(2, 3)
    fig.suptitle(f'BÁO CÁO KỸ NĂNG: {target_role.upper()}', fontsize=22, fontweight='bold', color='#2c3e50')

    # 1. BIỂU ĐỒ CỘT (Bar Chart) - Bên trái, chiếm 2 cột dọc
    ax1 = fig.add_subplot(gs[:, 0:2])
    y_pos = np.arange(len(skills))
    
    bars = ax1.barh(y_pos, percentages, color=colors, height=0.6)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([s.upper() for s in skills], fontsize=11)
    ax1.invert_yaxis() 
    ax1.set_xlabel('Tần suất xuất hiện trong tin tuyển dụng (%)', fontsize=12)
    ax1.set_title('🔥 Top 20 Kỹ năng Thị trường cần nhất', fontweight='bold', fontsize=14)
    ax1.grid(axis='x', linestyle='--', alpha=0.5)
    
    # Thêm label %
    for bar, p in zip(bars, percentages):
        ax1.text(p + 1, bar.get_y() + bar.get_height()/2, f'{p:.1f}%', va='center', fontsize=10, fontweight='bold')

    # 2. BIỂU ĐỒ DONUT (Góc trên phải)
    ax2 = fig.add_subplot(gs[0, 2])
    match_rate = (matches / len(skills)) * 100
    
    if len(skills) > 0:
        sizes = [matches, len(skills) - matches]
        labels = ['Đã có', 'Còn thiếu']
        ax2.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90, 
                colors=['#2ecc71', '#ecf0f1'], textprops={'fontsize': 12}, 
                wedgeprops=dict(width=0.4, edgecolor='w'))
        ax2.text(0, 0, f'{match_rate:.0f}%', ha='center', va='center', fontsize=24, fontweight='bold', color='#2c3e50')
        ax2.set_title('Độ phù hợp', fontweight='bold', fontsize=14)
    
    # 3. ROADMAP (Góc dưới phải)
    ax3 = fig.add_subplot(gs[1, 2])
    draw_roadmap(ax3, missing_data, num_jobs)

    # Lưu và hiện
    filename = f"report_{target_role.replace(' ', '_')}.png"
    plt.savefig(filename, dpi=100)
    print(f"\n📊 Đã lưu báo cáo đẹp vào file: '{filename}'")
    plt.show()

# --- 4. HÀM CHẠY CHÍNH ---
def run_analysis():
    student_skills, df_market = load_data()
    if student_skills is None: return

    target_role = input("\nNhập vị trí bạn muốn ứng tuyển (ví dụ: backend, data, devops): ").strip().lower()
    
    # Lọc dữ liệu
    df_filtered = df_market[df_market['Job_Title'].str.lower().str.contains(target_role, na=False)]
    num_jobs = len(df_filtered)
    
    if num_jobs == 0:
        print(f"⚠️ Không tìm thấy tin tuyển dụng nào cho '{target_role}'.")
        return

    print(f"🔍 Phân tích dựa trên {num_jobs} tin tuyển dụng.")

    all_skills = []
    for skills_str in df_filtered['Skills_Found'].dropna():
        if isinstance(skills_str, str):
            skills = [s.strip().lower() for s in skills_str.split(',')]
            all_skills.extend(skills)
    
    market_stats = Counter(all_skills).most_common(20)
    market_stats = [item for item in market_stats if item[0] != ""]

    # In text báo cáo
    print("\n--- KẾT QUẢ PHÂN TÍCH ---")
    print(f"{'TRẠNG THÁI':<10} | {'KỸ NĂNG':<20} | {'ĐỘ PHỔ BIẾN':<10}")
    print("-" * 45)
    for skill, count in market_stats:
        status = "✅ CÓ" if skill in student_skills else "❌ THIẾU"
        percent = (count / num_jobs) * 100
        print(f"{status:<10} | {skill:<20} | {percent:.1f}%")

    # Vẽ
    visualize_results(target_role, market_stats, student_skills, num_jobs)

if __name__ == "__main__":
    run_analysis()