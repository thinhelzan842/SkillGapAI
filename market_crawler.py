import pandas as pd
import time
from playwright.sync_api import sync_playwright

from skills_extractor import SkillExtractor
from skills_config import SKILL_DICTIONARY_MASTER_LIST as SKILL_DICTIONARY

print("--- KHỞI ĐỘNG HỆ THỐNG CRAWL & TRÍCH XUẤT ---")

# Khởi tạo extractor mạnh
extractor = SkillExtractor(SKILL_DICTIONARY)


# ==================================================
#  HÀM CRAWL TOPCV
# ==================================================
def crawl_topcv(num_pages_to_crawl=5):

    job_links = set()
    all_job_data = []

    base_url = "https://www.topcv.vn/tim-viec-lam-it?page="
    print(f"[CRAWL] Bắt đầu cào {num_pages_to_crawl} trang...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # ========================
            # VÒNG 1: LẤY TẤT CẢ LINK
            # ========================
            for i in range(1, num_pages_to_crawl + 1):
                url = base_url + str(i)
                print(f"  → Trang {i}")

                page.goto(url, wait_until="domcontentloaded", timeout=60000)

                page.wait_for_selector("div.job-item-search-result", timeout=15000)

                links = page.locator("h3.title a").all()

                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        job_links.add(href)

                time.sleep(1.2)

            print(f"\n[CRAWL] Tổng cộng {len(job_links)} link.")

            # ========================
            # VÒNG 2: CÀO CHI TIẾT JD
            # ========================
            count = 0
            for link in job_links:
                count += 1
                if not link.startswith("http"):
                    link = "https://www.topcv.vn" + link

                print(f"\n[{count}/{len(job_links)}] → {link[:60]}...")

                try:
                    page.goto(link, wait_until="domcontentloaded", timeout=60000)

                    # -----------------------
                    # Detect loại layout
                    # -----------------------
                    if "/brand/" in link:
                        title_selector = "h2.premium-job-basic-information__content--title"
                        jd_selector = "div.premium-job-description__box.job-detail-section.requirement"
                    else:
                        title_selector = "h1.job-detail__info--title"

                        # Thử nhiều selector vì TopCV đổi liên tục
                        jd_selectors_try = [
                            "div.job-description__item.job-detail-section.requirement",
                            "div.box-requirement",
                            "div.job-detail__box--requirement",
                            "div#job-detail-requirement"
                        ]

                    # -----------------------
                    # Lấy tiêu đề
                    # -----------------------
                    page.wait_for_selector(title_selector, timeout=15000)
                    title = page.locator(title_selector).inner_text().strip()

                    # -----------------------
                    # Lấy JD (thử nhiều selector)
                    # -----------------------
                    jd_text = None
                    if "/brand/" in link:
                        jd_text = page.locator(jd_selector).inner_text()
                    else:
                        for s in jd_selectors_try:
                            try:
                                jd_text = page.locator(s).inner_text()
                                if jd_text and len(jd_text.strip()) > 20:
                                    break
                            except:
                                pass

                    if not jd_text:
                        print("   [WARN] Không tìm thấy mục YÊU CẦU.")
                        continue

                    # -----------------------
                    # Extract skills bằng module mạnh
                    # -----------------------
                    skills_found = extractor.extract(jd_text)

                    all_job_data.append({
                        "Job_Title": title,
                        "Skills_Found": ", ".join(skills_found),
                        "JD_Text": jd_text[:300] + "...",
                        "URL": link
                    })

                    time.sleep(0.8)

                except Exception as e:
                    print(f"   [ERROR] Lỗi khi cào link: {e}")
                    continue

        finally:
            browser.close()

    return all_job_data


# ==================================================
#  MAIN - EXPORT CSV
# ==================================================
if __name__ == "__main__":
    data = crawl_topcv(num_pages_to_crawl=1)

    if data:
        df = pd.DataFrame(data)
        df.to_csv("market_requirements.csv", index=False, encoding="utf-8-sig")

        print("\n--- HOÀN THÀNH ---")
        print(f"Đã lưu {len(data)} tin tuyển dụng vào 'market_requirements.csv'")
    else:
        print("Không có dữ liệu để xuất.")
