# skills_config.py
# PHIÊN BẢN FINAL: MAPPING (ÁNH XẠ) ĐA NGÔN NGỮ

print("Đang tải 'bộ não' kỹ năng (Mapping Mode) từ skills_config.py...")

# --- TỪ ĐIỂN ÁNH XẠ (MAPPING) ---
# Cấu trúc: "TỪ_CHUẨN": ["từ đồng nghĩa 1", "từ đồng nghĩa 2", "tiếng việt", ...]
# Script sẽ tìm các từ bên phải, và lưu lại từ bên trái (Key).

SKILL_MAPPING = {
    # --- 1. PROGRAMMING LANGUAGES ---
    "python": ["python", "py", "pandas", "numpy", "scikit-learn", "pytorch", "tensorflow"], # Gộp các thư viện phổ biến vào
    "java": ["java", "java core", "j2ee", "spring", "spring boot", "hibernate", "jsp", "servlet"],
    "javascript": ["javascript", "js", "es6", "typescript", "node.js", "nodejs", "express"],
    "c#": ["c#", ".net", ".net core", "asp.net", "entity framework", "blazor", "winforms", "wpf"],
    "c++": ["c++", "cpp", "c plus plus", "lập trình c++"], # Tách riêng C++
    "c": ["c language", "lập trình c"],
    "php": ["php", "laravel", "symfony", "wordpress"],
    "go": ["go", "golang"],
    "ruby": ["ruby", "rails", "ruby on rails"],
    "swift": ["swift", "ios"],
    "kotlin": ["kotlin", "android"],
    "sql": ["sql", "t-sql", "pl/sql", "truy vấn", "cơ sở dữ liệu"],
    "mysql": ["mysql", "my sql"],
    "sql server": ["sql server", "mssql", "microsoft sql server"],
    "postgresql": ["postgresql", "postgres"],
    "oracle": ["oracle", "oracle db"],
    "mongodb": ["mongodb", "mongo"],
    "html/css": ["html", "html5", "css", "css3", "sass", "scss", "less", "tailwind", "bootstrap"],

    # --- 2. FRONTEND & MOBILE ---
    "react": ["react", "reactjs", "react.js", "react native", "redux", "next.js"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vuejs", "vue.js", "nuxt.js"],
    "mobile app": ["mobile app", "android", "ios", "flutter", "react native", "phát triển ứng dụng di động"],
    "ui/ux": ["ui", "ux", "user interface", "user experience", "figma", "adobe xd", "thiết kế giao diện"],

    # --- 3. BACKEND, CLOUD & DEVOPS ---
    "cloud": ["cloud", "aws", "amazon web services", "azure", "gcp", "google cloud", "điện toán đám mây"],
    "devops": ["devops", "ci/cd", "jenkins", "docker", "kubernetes", "k8s", "git", "gitlab", "github"],
    "microservices": ["microservices", "kiến trúc vi dịch vụ", "distributed systems"],
    "api": ["api", "rest", "restful", "graphql", "soap", "json"],
    "linux": ["linux", "unix", "ubuntu", "centos", "bash", "shell script"],

    # --- 4. DATA & AI ---
    "data science": ["data science", "khoa học dữ liệu", "data analysis", "phân tích dữ liệu"],
    "machine learning": ["machine learning", "học máy", "deep learning", "học sâu", "ai", "trí tuệ nhân tạo"],
    "big data": ["big data", "dữ liệu lớn", "hadoop", "spark", "kafka"],
    "database management": ["database management", "quản trị cơ sở dữ liệu", "dbms", "database design", "mongodb", "redis", "elasticsearch"],

    # --- 5. BUSINESS & DOMAIN (QUAN TRỌNG) ---
    "business analyst": ["business analyst", "ba", "phân tích nghiệp vụ", "lấy yêu cầu", "srs", "uml"],
    "project management": ["project management", "quản trị dự án", "pm", "agile", "scrum", "kanban", "jira"],
    "software engineering": ["software engineering", "công nghệ phần mềm", "quy trình phần mềm", "sdlc", "waterfall"],
    "testing": ["testing", "kiểm thử", "qa", "qc", "test case", "automation test", "selenium"],
    "security": ["security", "bảo mật", "an toàn thông tin", "cybersecurity", "pentest"],
    "e-commerce": ["e-commerce", "thương mại điện tử"],
    "banking": ["banking", "ngân hàng", "fintech"],

    # --- 6. SOFT SKILLS (VIỆT HÓA) ---
    "communication": ["communication", "giao tiếp", "thuyết trình", "trình bày", "trao đổi", "đàm phán"],
    "teamwork": ["teamwork", "làm việc nhóm", "hợp tác", "cộng tác", "team player"],
    "problem solving": ["problem solving", "giải quyết vấn đề", "xử lý sự cố", "tư duy logic", "logical thinking"],
    "critical thinking": ["critical thinking", "tư duy phản biện"],
    "self-learning": ["self-learning", "tự học", "nghiên cứu", "khả năng học hỏi", "research"],
    "english": ["english", "tiếng anh", "đọc hiểu tài liệu", "ielts", "toeic"],
    "leadership": ["leadership", "lãnh đạo", "quản lý nhóm", "team lead"],
}

# --- TẠO DANH SÁCH TỔNG (Dùng cho Script 1 - Fuzzy Matching) ---
SKILL_DICTIONARY_MASTER_LIST = list(SKILL_MAPPING.keys())

# --- PHÂN LOẠI (Dùng cho Script 3 - Gap Analysis) ---
# Tự động phân loại dựa trên các key ở trên
SOFT_BUSINESS_KEYS = [
    "communication", "teamwork", "problem solving", "critical thinking", 
    "self-learning", "english", "leadership", 
    "business analyst", "project management", "e-commerce", "banking"
]

SOFT_BUSINESS_SKILLS = set(SOFT_BUSINESS_KEYS)
HARD_SKILLS = set([k for k in SKILL_MAPPING.keys() if k not in SOFT_BUSINESS_KEYS])

print(f"Đã tải 'bộ não' chuẩn với {len(SKILL_DICTIONARY_MASTER_LIST)} kỹ năng chính.")

# Hàm hỗ trợ chuẩn hóa (Dùng cho Script 2)
def normalize_skill(raw_text):
    raw_text = str(raw_text).lower().strip()
    for standard, synonyms in SKILL_MAPPING.items():
        # Kiểm tra chính xác trước
        if raw_text == standard:
            return standard
        # Kiểm tra từ đồng nghĩa
        if raw_text in synonyms:
            return standard
        # Kiểm tra chứa (cẩn thận hơn)
        for syn in synonyms:
             # Thêm khoảng trắng để tránh match nhầm (ví dụ "java" trong "javascript")
             if f" {syn} " in f" {raw_text} ": 
                 return standard
    return raw_text