import pandas as pd
from sentence_transformers import SentenceTransformer, util
import warnings
from fuzzywuzzy import process

# Tắt cảnh báo
warnings.filterwarnings("ignore")

# --- BƯỚC 1: TẢI "BỘ NÃO" CHUẨN TỪ FILE CONFIG ---
try:
    from skills_config import (
        SKILL_DICTIONARY_MASTER_LIST as MASTER_SKILL_LIST,
    )
    print("--- KHỞI ĐỘNG HỆ THỐNG SUY LUẬN KỸ NĂNG (v10.1 - Final) ---")
    print(f"  ✅ Đã tải 'bộ não' chuẩn từ skills_config.py")
except ImportError:
    print("❌ LỖI: Không tìm thấy file 'skills_config.py'.")
    exit()

# --- BƯỚC 2: KHỞI TẠO KNOWLEDGE BASE (Ánh xạ Môn học -> Kỹ năng Chuẩn) ---

# 1. CONCEPT_MAP: Các môn có kỹ năng rõ ràng, không cần hỏi lại
CONCEPT_MAP = {
    # =================================================================
    # PHẦN 1: MÔN HỌC FPT (Giữ nguyên để khớp bảng điểm của bạn)
    # =================================================================
    "Elementary Business English": ["english", "communication"],
    "Pre-Intermediate Business English": ["english", "communication"],
    "Intermediate Business English": ["english", "presentation"],
    "Upper-Intermediate Business English": ["english", "negotiation"],
    "Japanese Elementary 1": ["japanese", "n5"],
    "Japanese Elementary 2": ["japanese", "n5"],
    "Japanese Elementary 3": ["japanese", "n5", "n4"],
    "Japanese Elementary 4": ["japanese", "n4"],
    "Business Communication Skills": ["communication", "presentation", "soft skills"],
    "Working in Group Skills": ["teamwork", "soft skills"],
    "Ethics in Information Technology": ["security", "information security"],
    "Principles of Accounting and Finance": ["accounting", "fintech"],
    "E-commerce": ["e-commerce"],
    "Advanced Mathematics 1": ["logical thinking"],
    "Advanced Mathematics 2": ["logical thinking", "matrix"],
    "Discrete Mathematics": ["logical thinking", "algorithms"],
    "Probability and Applied Statistics": ["statistics", "data analysis"],
    "Introduction to Computing": ["computer architecture", "operating systems", "network"],
    "Programming with Alice": ["visual programming", "logical thinking", "oop"],
    "Operating Systems": ["operating systems", "linux", "process management"],
    "Computer Network": ["network", "tcp/ip", "osi model"],
    "Introduction to Software Engineering": ["software engineering", "agile", "uml"],
    "Software Requirements": ["requirements engineering", "srs", "use cases"],
    "Software Quality Assurance & Testing": ["testing", "qa", "qc"],
    "Human Computer Interaction": ["hci", "ui/ux", "usability"],
    "IT Project Management": ["project management", "agile", "scrum"],
    "Software Architecture and Design": ["software architecture", "design patterns", "solid"],
    "Capstone Project": ["project management", "teamwork", "fullstack", "problem solving"],

    # =================================================================
    # PHẦN 2: MÔN HỌC HCMUS (Trích xuất từ CTĐT K2024)
    # =================================================================
    
    # --- 1. Giáo dục Đại cương & Lý luận ---
    "Triết học Mác - Lênin": ["critical thinking"],
    "Kinh tế chính trị Mác - Lênin": ["critical thinking", "economics"],
    "Chủ nghĩa xã hội khoa học": ["critical thinking"],
    "Lịch sử Đảng Cộng sản Việt Nam": ["critical thinking"],
    "Tư tưởng Hồ Chí Minh": ["critical thinking"],
    "Pháp luật đại cương": ["law"],
    "Kinh tế đại cương": ["economics"],
    "Tâm lý đại cương": ["soft skills", "communication"],
    "Phương pháp luận sáng tạo": ["problem solving", "creativity"],
    
    # --- 2. Toán & Khoa học Tự nhiên ---
    "Vi tích phân 1": ["logical thinking", "calculus"],
    "Vi tích phân 2": ["logical thinking", "calculus"],
    "Đại số tuyến tính": ["logical thinking", "linear algebra", "matrix"],
    "Xác suất thống kê": ["statistics", "data analysis", "probability"],
    "Toán rời rạc": ["logical thinking", "discrete math", "graph theory"],
    "Toán học tổ hợp": ["algorithms", "combinatorics"],
    "Toán ứng dụng và thống kê": ["statistics", "data analysis"],
    "Phương pháp tính": ["numerical methods", "algorithms"],
    "Lý thuyết số": ["number theory", "cryptography"],
    "Vật lý đại cương 1 (Cơ - Nhiệt)": ["physics"],
    "Vật lý đại cương 2 (Điện từ - Quang)": ["physics"],
    "Hóa đại cương 1": ["chemistry"],
    "Sinh đại cương 1": ["biology"],
    
    # --- 3. Ngoại ngữ & Kỹ năng ---
    "Anh văn 1": ["english"], "Anh văn 2": ["english"], 
    "Anh văn 3": ["english"], "Anh văn 4": ["english"],
    "Kỹ năng mềm": ["soft skills", "communication", "teamwork", "time management"],
    "Kiến tập nghề nghiệp": ["internship", "soft skills"],
    "Khởi nghiệp": ["startup", "business", "entrepreneurship"],
    
    # --- 4. Cơ sở ngành (Cốt lõi) ---
    "Nhập môn Công nghệ thông tin": ["it fundamentals"],
    "Tư duy tính toán": ["computational thinking", "logical thinking"],
    "Hệ thống máy tính": ["computer architecture", "assembly"],
    "Nhập môn công nghệ phần mềm": ["software engineering", "sdlc", "agile"],
    "Cơ sở trí tuệ nhân tạo": ["ai", "artificial intelligence", "search algorithms", "logic"],
    
    # --- 5. Chuyên ngành: Mạng & Viễn thông ---
    "Hệ thống viễn thông": ["telecommunications"],
    "Lập trình mạng": ["network programming", "sockets", "tcp/ip"],
    "Mạng máy tính nâng cao": ["network", "routing", "switching", "vlan"],
    "Nhập môn điện toán đám mây": ["cloud", "aws", "azure", "gcp"],
    "Nhập môn DevOps": ["devops", "ci/cd", "docker", "git"],
    "DevOps nâng cao": ["devops", "kubernetes", "jenkins", "infrastructure as code"],
    "An ninh mạng": ["network security", "firewall", "vpn"],
    "An ninh máy tính": ["security", "cybersecurity"],
    "Truyền thông không dây": ["wireless", "mobile network"],
    "Hệ điều hành Linux và ứng dụng": ["linux", "bash", "shell script"],
    "Triển khai và vận hành điện toán đám mây": ["cloud", "deployment", "operations"],
    "Bảo mật web và thiết bị di động": ["web security", "mobile security", "owasp"],
    "Mã hóa ứng dụng": ["cryptography", "encryption"],
    "Nhập môn mã hóa – mật mã": ["cryptography", "encryption"],
    
    # --- 6. Chuyên ngành: Hệ thống thông tin ---
    "An toàn và bảo mật dữ liệu trong hệ thống thông tin": ["data security", "information security"],
    "Cơ sở dữ liệu nâng cao": ["database management", "sql", "stored procedure", "trigger"],
    "Hệ quản trị cơ sở dữ liệu": ["dbms", "sql server", "oracle", "postgresql"],
    "Phân tích thiết kế hệ thống thông tin": ["system analysis", "design", "uml", "database design"],
    "Phát triển ứng dụng hệ thống thông tin hiện đại": ["information systems", "application development"],
    "Trực quan hóa dữ liệu": ["data visualization", "tableau", "power bi"],
    "Thương mại điện tử": ["e-commerce", "digital business"],
    "Tương tác người – máy": ["hci", "ui/ux", "user experience"],
    "Hệ thống thông tin doanh nghiệp": ["erp", "enterprise systems"],
    "Phân tích dữ liệu ứng dụng": ["data analysis"],
    "Hệ thống tư vấn": ["recommender systems", "ai"],
    "Xử lý phân tích dữ liệu trực tuyến": ["olap", "data warehousing"],
    
    # --- 7. Chuyên ngành: Kỹ thuật phần mềm ---
    "Kiểm thử phần mềm": ["testing", "qa", "automation testing", "test case"],
    "Phân tích và quản lý yêu cầu phần mềm": ["requirements engineering", "business analyst", "srs"],
    "Quản lý dự án phần mềm": ["project management", "scrum", "jira"],
    "Phát triển game": ["game development", "unity", "c#"],
    "Phát triển game nâng cao": ["game development", "unreal engine", "3d math"],
    "Thiết kế phần mềm": ["software design", "design patterns", "solid"],
    "Kiến trúc phần mềm": ["software architecture", "microservices", "design patterns"],
    "Thiết kế giao diện": ["ui/ux", "figma", "design"],
    "Lập trình Windows": ["c#", ".net", "winforms", "wpf"],
    "Các chủ đề nâng cao trong Công nghệ phần mềm": ["software engineering"],
    "Nhập môn hệ thống phân tán": ["distributed systems"],
    "Mẫu thiết kế hướng đối tượng và ứng dụng": ["design patterns", "oop"],
    "Nhập môn lập trình điều khiển thiết bị thông minh": ["iot", "embedded systems"],
    
    # --- 8. Chuyên ngành: Khoa học máy tính & AI ---
    "Automata và ngôn ngữ hình thức": ["automata", "formal languages", "compiler design"],
    "Các hệ cơ sở tri thức": ["knowledge base", "expert systems"],
    "Khai thác dữ liệu và ứng dụng": ["data mining", "data analysis"],
    "Nhập môn học máy": ["machine learning", "scikit-learn", "python"],
    "Nhận dạng": ["pattern recognition"],
    "Ẩn dữ liệu và chia sẻ thông tin": ["steganography", "information hiding"],
    "Nhập môn thiết kế và phân tích giải thuật": ["algorithms", "complexity analysis"],
    "Nhập môn dữ liệu lớn": ["big data", "hadoop", "spark"],
    "Lập trình song song": ["parallel computing", "cuda", "multi-threading"],
    "Nhập môn xử lý ngôn ngữ tự nhiên": ["nlp", "text processing"],
    "Thị giác máy tính": ["computer vision", "opencv", "image processing"],
    "Trí tuệ nhân tạo cho an ninh thông tin": ["ai", "security"],
    "Phương pháp toán cho tối ưu": ["optimization", "mathematics"],
    "Trí tuệ bầy đàn": ["swarm intelligence", "ai"],
    "Nhập môn hệ thống đa tác nhân": ["multi-agent systems", "ai"],
    "Phương pháp nghiên cứu khoa học": ["research methods"],
    "Khoa học về web": ["web science", "semantic web"],
    "Sinh trắc học": ["biometrics"],
    "Trình biên dịch": ["compilers"],
    "Nhập môn lập trình kết nối vạn vật": ["iot", "arduino", "raspberry pi"],
    "Nhập môn khoa học dữ liệu": ["data science", "python", "pandas"],
    "Xử lý ảnh số và video số": ["image processing", "video processing"],
    "Phân tích dữ liệu thông minh": ["data analysis", "ai"],
    "Khai thác dữ liệu đồ thị": ["graph mining", "data mining"],
    "Nhập môn học sâu": ["deep learning", "neural networks", "pytorch", "tensorflow"],
    "Blockchain và ứng dụng": ["blockchain", "smart contracts"],
    "Phân tích mạng xã hội": ["social network analysis", "graph theory"],
    "Pháp chứng cho dữ liệu số": ["digital forensics"],
    "Đồ họa máy tính": ["computer graphics", "opengl"],
    "Đồ họa ứng dụng": ["computer graphics", "design"],
    "Truy vấn thông tin thị giác": ["information retrieval", "computer vision"],
    "Ứng dụng thị giác máy tính": ["computer vision", "ai application"],
    
    # --- 9. Tốt nghiệp & Chuyên đề ---
    "Khóa luận tốt nghiệp": ["research", "project management", "writing"],
    "Thực tập tốt nghiệp": ["internship", "working experience"],
    "Thực tập dự án tốt nghiệp": ["project management", "teamwork"],
    "Chuyên đề tốt nghiệp Mạng máy tính": ["network"],
    "Chuyên đề Hệ thống phân tán": ["distributed systems"],
    "Chuyên đề phân tích mạng": ["network analysis", "wireshark"],
    "Chuyên đề Đồ họa máy tính": ["computer graphics"],
    "Chuyên đề Thị giác máy tính": ["computer vision"],
    "Chuyên đề Xử lý ảnh số và video số": ["image processing"],
}

# 2. EVIDENCE_MAP: Các môn tiết lộ công nghệ cụ thể (Gộp FPT + HCMUS)
EVIDENCE_MAP = {
    # FPT
    "Core Java": {"skills": ["java"], "tech": "java"},
    "Advanced Java": {"skills": ["java", "spring"], "tech": "java"},
    "C# and .NET": {"skills": ["c#", ".net"], "tech": "c#"},
    "Advanced XML": {"skills": ["xml"], "tech": "xml"},
    # HCMUS
    "Lập trình ứng dụng Java": {"skills": ["java"], "tech": "java"},
    "Lập trình Windows": {"skills": ["c#", ".net", "winforms"], "tech": "c#"},
    "Lập trình Web 1": {"skills": ["html/css", "javascript"], "tech": "web"},
    "Lập trình Web 2": {"skills": ["php", "laravel", "node.js"], "tech": "web"},
    "Phát triển ứng dụng web": {"skills": ["html/css", "javascript", "backend"], "tech": "web"},
    "Phát triển phần mềm cho thiết bị di động": {"skills": ["mobile app", "android", "ios"], "tech": "mobile"},
    "Lập trình cho khoa học dữ liệu": {"skills": ["python", "pandas", "numpy"], "tech": "python"},
    "Nhập môn điện toán đám mây": {"skills": ["cloud", "aws", "azure"], "tech": "cloud"},
    "Hệ điều hành Linux và ứng dụng": {"skills": ["linux", "bash"], "tech": "linux"},
}

# 3. AMBIGUOUS_MAP: Các môn chung chung cần hỏi người dùng
AMBIGUOUS_MAP = {
    # FPT + HCMUS (Chung logic)
    "Programming Fundamental": {
        "skills": ["logical thinking"],
        "prompt": "❓ Bạn đã học ngôn ngữ nào cho môn 'Programming Fundamental' (ví dụ: C, Python)?"
    },
    "Cơ sở lập trình": {
        "skills": ["logical thinking"],
        "prompt": "❓ Bạn đã học ngôn ngữ nào cho môn 'Cơ sở lập trình' (ví dụ: C, C++, Python)?"
    },
    "Object Oriented Programming": {
        "skills": ["c#", "java", "c++"], # Gợi ý các ngôn ngữ OOP phổ biến
        "prompt": "❓ Bạn đã học ngôn ngữ nào cho môn 'Object Oriented Programming' (ví dụ: Java, C#)?"
    },
    "Phương pháp lập trình hướng đối tượng": {
        "skills": ["c#", "java", "c++"],
        "prompt": "❓ Bạn đã học ngôn ngữ nào cho môn 'Phương pháp lập trình hướng đối tượng' (ví dụ: Java, C#)?"
    },
    "Data Structure and Algorithms": {
        "skills": ["algorithms"],
        "prompt": "❓ Bạn đã dùng ngôn ngữ nào để học 'Data Structure and Algorithms'?"
    },
    "Cấu trúc dữ liệu và giải thuật": {
        "skills": ["algorithms"],
        "prompt": "❓ Bạn đã dùng ngôn ngữ nào để học 'Cấu trúc dữ liệu và giải thuật'?"
    },
    "Introduction to Databases": {
        "skills": ["sql", "database management"],
        "prompt": "❓ Bạn đã học HỆ CSDL nào cho môn 'Introduction to Databases' (ví dụ: MySQL, SQL Server)?"
    },
    "Advanced Database": {
        "skills": ["database administration", "performance tuning", "sql"],
        "prompt": "❓ Bạn đã học HỆ CSDL nào cho môn 'Advanced Database' (ví dụ: Oracle, PostgreSQL, NoSQL)?"
    },
    "Cơ sở dữ liệu": {
        "skills": ["sql", "database management"],
        "prompt": "❓ Bạn đã học HỆ CSDL nào cho môn 'Cơ sở dữ liệu' (ví dụ: MySQL, SQL Server)?"
    },
}

# --- BƯỚC 3: TẢI MÔ HÌNH AI ---
print("[1/4] Đang tải mô hình AI...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# --- BƯỚC 4: MÃ HÓA "BỘ NÃO" MÔN HỌC ---
print("[2/4] Đang mã hóa Bộ não Môn học...")
all_kb_courses = list(CONCEPT_MAP.keys()) + list(EVIDENCE_MAP.keys()) + list(AMBIGUOUS_MAP.keys())
all_kb_embeddings = model.encode(all_kb_courses)
print(f"  ✅ Đã mã hóa {len(all_kb_courses)} môn học chuẩn.")

# --- BƯỚC 5: ĐỌC BẢNG ĐIỂM ---
file_path = 'transcript.csv'
print(f"[3/4] Đang đọc bảng điểm '{file_path}'...")
try:
    df = pd.read_csv(file_path)
    if 'Subject' not in df.columns:
        print("LỖI: File CSV phải có cột 'Subject'.")
        exit()
    student_courses = df['Subject'].tolist()
    student_embeddings = model.encode(student_courses)
except FileNotFoundError:
    print(f"LỖI: Không tìm thấy '{file_path}'.")
    exit()

# --- BƯỚC 6: SO KHỚP & TRÍCH XUẤT ---
print("[4/4] Đang so khớp và trích xuất kỹ năng...")
final_skills = set()
detected_technologies = set()
ambiguous_to_ask = []
SIMILARITY_THRESHOLD = 0.75 

matches = util.semantic_search(student_embeddings, all_kb_embeddings, top_k=1)
matched_student_courses = set()

for i in range(len(student_courses)):
    student_course = student_courses[i]
    best_match = matches[i][0]
    score = best_match['score']
    kb_course = all_kb_courses[best_match['corpus_id']]

    # Ưu tiên khớp chính xác 100%
    if student_course in all_kb_courses:
        kb_course = student_course
        score = 1.0
    
    if score >= SIMILARITY_THRESHOLD:
        # Logic lấy kỹ năng (Mapping)
        if kb_course in EVIDENCE_MAP:
            data = EVIDENCE_MAP[kb_course]
            final_skills.update(data['skills'])
            detected_technologies.add(data['tech'])
        
        elif kb_course in CONCEPT_MAP:
            final_skills.update(CONCEPT_MAP[kb_course])
        
        elif kb_course in AMBIGUOUS_MAP:
            if student_course not in matched_student_courses:
                data = AMBIGUOUS_MAP[kb_course]
                final_skills.update(data['skills'])
                ambiguous_to_ask.append((student_course, data['prompt']))
                matched_student_courses.add(student_course)
        
        if score < 1.0:
             print(f"  [AI Match] '{student_course}' ≈ '{kb_course}' ({score:.2f})")

# --- VÒNG HỎI (INTERACTIVE) ---
if ambiguous_to_ask:
    print(f"\n--- HỆ THỐNG CẦN XÁC NHẬN ({len(ambiguous_to_ask)} môn) ---")
    if detected_technologies:
        print(f"💡 Gợi ý từ các môn khác: {', '.join(detected_technologies)}")
    
    for course, prompt in ambiguous_to_ask:
        ans = input(f"{prompt} (Môn: {course}): ").strip()
        if ans:
            cleaned_answer = ans.lower()
            
            # --- LOGIC SỬA LỖI C++ ---
            # Kiểm tra chính xác trước khi dùng Fuzzy Match
            if cleaned_answer in MASTER_SKILL_LIST:
                final_skills.add(cleaned_answer)
                print(f"  ✅ Đã thêm chính xác: '{cleaned_answer}'")
                continue 
            
            # Nếu không khớp chính xác, mới dùng Fuzzy
            best_match, score = process.extractOne(cleaned_answer, MASTER_SKILL_LIST)
            if score >= 80:
                final_skills.add(best_match)
                print(f"  ✅ Đã thêm (Fuzzy): {best_match}")
            else:
                final_skills.add(cleaned_answer)
                print(f"  ⚠️ Thêm mới: {cleaned_answer}")

# --- XUẤT FILE ---
try:
    df_out = pd.DataFrame(sorted(list(final_skills)), columns=['Extracted_Skill'])
    df_out.to_csv('extracted_skills.csv', index=False, encoding='utf-8-sig')
    print(f"\n✅ HOÀN TẤT! Đã lưu {len(final_skills)} kỹ năng vào 'extracted_skills.csv'.")
except Exception as e:
    print(f"Lỗi khi lưu file: {e}")