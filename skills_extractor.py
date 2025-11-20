import re
import unicodedata

class SkillExtractor:
    def __init__(self, skill_dictionary):
        """
        skill_dictionary: list skill gốc của bạn
        """
        self.skill_dict = skill_dictionary
        self.regex_map = self._build_regex_patterns(skill_dictionary)

    # ---------------------------------------
    # 1) Chuẩn hoá văn bản
    # ---------------------------------------
    def normalize_text(self, text):
        if not text:
            return ""
        text = text.lower()

        # Bỏ dấu tiếng Việt
        text = unicodedata.normalize("NFD", text)
        text = "".join([c for c in text if unicodedata.category(c) != "Mn"])

        # Thay mọi ký tự phân cách có thể thành khoảng trắng
        text = re.sub(r"[\n\r\t/|\\\-\_]", " ", text)

        # Gom nhiều dấu cách → 1 dấu cách
        text = re.sub(r"\s+", " ", text)
        return f" {text.strip()} "

    # ---------------------------------------
    # 2) Tạo regex thông minh cho từng skill
    # ---------------------------------------
    def _build_regex_patterns(self, skills):
        patterns = {}

        for skill in skills:
            escaped = re.escape(skill.lower())

            if skill.lower() == "c":
                p = r"(?<!c\+\+)(?<!c\s\+\+)(?<!objective\-c)(?<!objc)\bc\b(?!\+\+)"
            elif skill.lower() == "c++":
                p = r"\bc\+\+\b"
            elif skill.lower() in ["js", "javascript"]:
                p = r"\bjava\s*script\b|\bjs\b"
            elif skill.lower() == "nodejs":
                p = r"\bnode\s*js\b|\bnodejs\b|\bnode\.js\b"
            else:
                p = rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"

            patterns[skill] = re.compile(p)

        return patterns

    # ---------------------------------------
    # 3) Hàm extract skill chính
    # ---------------------------------------
    def extract(self, text):
        if not text:
            return []

        norm = self.normalize_text(text)
        found = []

        for skill, pattern in self.regex_map.items():
            if pattern.search(norm):
                found.append(skill)

        return found
