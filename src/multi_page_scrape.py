# -------------------- IMPORTS -------------------- #
import time
import pandas as pd
from multiprocessing import Pool, cpu_count
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from src.crawl_url import crawl_peptide_urls

# -------------------- CONFIG -------------------- #
URLS = crawl_peptide_urls()
# URLS = ["https://pep-pedia.org/peptides/adalank"]  # limit for testing, remove or adjust as needed
TIMEOUT = 8
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
MASTER_CSV = OUTPUT_DIR / "pep_pedia_master.csv"
ERROR_LOG = OUTPUT_DIR / "error_log.txt"

# -------------------- DRIVER SETUP -------------------- #
def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, TIMEOUT)
    return driver, wait

# -------------------- UTILITIES -------------------- #
def safe_click(driver, wait, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        wait.until(EC.element_to_be_clickable(element)).click()
    except:
        driver.execute_script("arguments[0].click();", element)

def get_categories(driver, wait):
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10")))
    buttons = driver.find_elements(By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10 button")
    return [b.text.strip() for b in buttons if b.text.strip()]

def get_hero_data(driver, wait):
    hero = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.peptide-hero-gradient")))
    name = hero.find_element(By.TAG_NAME, "h1").text.strip()
    subtitle = hero.find_element(By.TAG_NAME, "p").text.strip()
    facts = []
    cards = hero.find_elements(By.XPATH, ".//div[contains(@class,'rounded-2xl')]")
    for card in cards:
        lines = [l.strip() for l in card.text.split("\n") if l.strip()]
        if len(lines) >= 2:
            facts.append({
                "label": lines[0],
                "value": lines[1],
                "extra": lines[2] if len(lines) > 2 else ""
            })
    return {"name": name, "subtitle": subtitle, "facts": facts}

def get_quick_guide(driver, wait):
    try:
        guide = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h3[contains(text(),'Quick Start Guide')]/ancestor::div[contains(@class,'rounded-xl')]")
        ))
        rows = guide.find_elements(By.CSS_SELECTOR, "div.flex.gap-3")
        return { 
            r.find_element(By.CSS_SELECTOR, ".text-label-sm").text.strip():
            r.find_element(By.CSS_SELECTOR, ".text-body-sm").text.strip()
            for r in rows
        }
    except TimeoutException:
        return {}

def get_sections(driver, wait):
    data = []
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.mb-12")))
        for section in driver.find_elements(By.CSS_SELECTOR, "section.mb-12"):
            section_data = []

            # ---- STATIC TEXT ----
            for el in section.find_elements(By.XPATH, ".//h2|.//h3|.//h4|.//p|.//table|.//li|.//pre|.//ol"):
                text = el.text.strip()
                if text:
                    section_data.append({"type": el.tag_name, "text": text})

            # ---- ACCORDIONS ----
            buttons = section.find_elements(By.CSS_SELECTOR, "button[data-state]")
            for btn in buttons:
                title = btn.text.strip()
                panel_id = btn.get_attribute("aria-controls")

                if btn.get_attribute("data-state") == "closed":
                    safe_click(driver, wait, btn)

                try:
                    panel = wait.until(EC.visibility_of_element_located((By.ID, panel_id)))
                    content = panel.text.strip()
                    section_data.append({"dropdown": title, "content": content})
                except:
                    continue

            data.append(section_data)
    except TimeoutException:
        pass
    return data

# -------------------- SCRAPE SINGLE URL -------------------- #
def scrape_url(url):
    driver, wait = create_driver()
    start_time = time.time()
    try:
        print(f"[INFO] Processing: {url}")
        driver.get(url)
        time.sleep(2)

        results = {}
        categories = get_categories(driver, wait)

        for cat in categories:
            buttons = driver.find_elements(By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10 button")
            for b in buttons:
                if b.text.strip() == cat:
                    safe_click(driver, wait, b)
                    break
            time.sleep(1)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.peptide-hero-gradient")))

            results[cat] = {
                "hero": get_hero_data(driver, wait),
                "quick_guide": get_quick_guide(driver, wait),
                "sections": get_sections(driver, wait),
                "url": driver.current_url
            }

        # Convert results to rows
        rows = []
        for cat, content in results.items():
            hero = content.get("hero", {})
            row = {"Peptide_Name": hero.get("name", ""),
                   "Full_Name": hero.get("subtitle", ""),
                   "Method": cat}
            for fact in hero.get("facts", []):
                col_name = fact["label"].replace(" ", "_").lower()
                row[f"{col_name}"] = fact["value"]

            for k, v in content.get("quick_guide", {}).items():
                col_name = k.replace(" ", "_").lower()
                row[f"{col_name}"] = v

            # for section in content.get("sections", []):
            #     h2_title = None
            #     section_texts = []

            #     for item in section:
            #         if item.get("type") == "h2":
            #             if h2_title and section_texts:
            #                 row[h2_title] = "\n".join(section_texts)
            #             h2_title = item["text"].replace(" ", "_").lower()
            #             section_texts = []
            #         elif item.get("type") in ["p", "li"]:
            #             section_texts.append(item["text"])
            #         elif "dropdown" in item:
            #             acc_title = item["dropdown"].replace(" ", "_").lower()
            #             row[f"{h2_title}_{acc_title}" if h2_title else acc_title] = item["content"]

            #     if h2_title and section_texts:
            #         row[h2_title] = "\n".join(section_texts)

            for section in content.get("sections", []):
                h2_title = None
                section_texts = []

                for item in section:
                    # h2 → column name
                    if item.get("type") == "h2":
                        # Save previous h2 content if exists
                        if h2_title:
                            row[h2_title] = "\n".join(section_texts)
                        h2_title = item["text"].replace(" ", "_").lower()
                        section_texts = []
                    else:
                        # Take text if exists, otherwise content (for dropdowns)
                        text = item.get("text", "")
                        content_val = item.get("content", "")
                        combined = "\n".join([t for t in [text, content_val] if t.strip()])
                        if combined:
                            section_texts.append(combined)

                # Save last h2 section
                if h2_title:
                    row[h2_title] = "\n".join(section_texts)

            row["scrape_time_seconds"] = round(time.time() - start_time, 2)  # track time
            print(f"[INFO] Finished {url} in {row['scrape_time_seconds']} seconds")
            print(f"remaining URLs: {len(URLS) - URLS.index(url) - 1}")
            row["URL"] = url  # original URL for reference
            rows.append(row)

        return rows, None  # success, no error

    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return [], f"{url} - {e}"  # empty rows, log error
    finally:
        driver.quit()

# -------------------- MULTIPROCESSING -------------------- #
if __name__ == "__main__":
    start_total = time.time()
    all_rows = []
    error_logs = []

    def process_result(result):
        rows, error = result
        if rows:
            all_rows.extend(rows)
        if error:
            error_logs.append(error)

    with Pool(processes=min(cpu_count(), 8)) as pool:
        for result in pool.imap_unordered(scrape_url, URLS):
            process_result(result)
    # with Pool(processes=min(cpu_count(), 4)) as pool:
    #     results = pool.map(scrape_url, URLS)  # each URL is processed once

    # Save master CSV
    pd.DataFrame(all_rows).to_csv(MASTER_CSV, index=False)
    print(f"[INFO] Master CSV saved at {MASTER_CSV}")

    # Save error log
    if error_logs:
        with open(ERROR_LOG, "w") as f:
            for line in error_logs:
                f.write(line + "\n")
        print(f"[INFO] Errors logged at {ERROR_LOG}")

    print(f"[INFO] Total scraping time: {round(time.time() - start_total, 2)} seconds")
