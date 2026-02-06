from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import pandas as pd
import time

# ---------------- CONFIG ---------------- #
URLS = [
    "https://pep-pedia.org/peptides/adalank",
    "https://pep-pedia.org/peptides/adamax",
    "https://pep-pedia.org/peptides/adipotide",
    "https://pep-pedia.org/peptides/ahk-cu",
    "https://pep-pedia.org/peptides/aod-9604",
    "https://pep-pedia.org/peptides/5-amino-1mq",
    "https://pep-pedia.org/peptides/omberacetam",
    "https://pep-pedia.org/peptides/ara-290",
    "https://pep-pedia.org/peptides/bioglutide",
    "https://pep-pedia.org/peptides/bpc-157",
    "https://pep-pedia.org/peptides/cagrilintide"

    # add more URLs here
]
TIMEOUT = 8

# --------------- DRIVER SETUP --------------- #
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, TIMEOUT)

# ---------------- UTILITIES ---------------- #

def safe_click(element):
    """Reliable click with scroll + JS fallback"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        wait.until(EC.element_to_be_clickable(element)).click()
    except:
        driver.execute_script("arguments[0].click();", element)


def get_categories():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10")))
    buttons = driver.find_elements(By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10 button")
    return [b.text.strip() for b in buttons if b.text.strip()]


def get_hero_data():
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


def get_quick_guide():
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


def get_sections():
    data = []
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.mb-12")))
        for section in driver.find_elements(By.CSS_SELECTOR, "section.mb-12"):
            section_data = []

            # ---- STATIC TEXT ----
            for el in section.find_elements(By.XPATH, ".//h2|.//h3|.//h4|.//p|.//li"):
                text = el.text.strip()
                if text:
                    section_data.append({"type": el.tag_name, "text": text})

            # ---- ACCORDIONS ----
            buttons = section.find_elements(By.CSS_SELECTOR, "button[data-state]")
            for btn in buttons:
                title = btn.text.strip()
                panel_id = btn.get_attribute("aria-controls")

                if btn.get_attribute("data-state") == "closed":
                    safe_click(btn)

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


# ---------------- BATCH SCRAPING ---------------- #

all_data = []

for url in URLS:
    print(f"\n Processing: {url}")
    driver.get(url)
    time.sleep(2)  # small wait to ensure page loads

    results = {}
    categories = get_categories()

    for cat in categories:
        # Click category safely
        buttons = driver.find_elements(By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10 button")
        for b in buttons:
            if b.text.strip() == cat:
                safe_click(b)
                break

        time.sleep(1)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.peptide-hero-gradient")))

        results[cat] = {
            "hero": get_hero_data(),
            "quick_guide": get_quick_guide(),
            "sections": get_sections(),
            "url": driver.current_url
        }

    # ---- CONVERT RESULTS TO DATAFRAME-LIKE ROWS ----
    for cat, content in results.items():
        row = {"category": cat, "url": content.get("url", url)}

        # Hero
        hero = content.get("hero", {})
        row["hero_name"] = hero.get("name", "")
        row["hero_subtitle"] = hero.get("subtitle", "")
        for fact in hero.get("facts", []):
            col_name = fact["label"].replace(" ", "_").lower()
            row[f"hero_{col_name}"] = fact["value"]

        # Quick Guide
        for k, v in content.get("quick_guide", {}).items():
            col_name = k.replace(" ", "_").lower()
            row[f"quick_{col_name}"] = v

        # Sections
        for section in content.get("sections", []):
            h2_title = None
            section_texts = []

            for item in section:
                if item.get("type") == "h2":
                    if h2_title and section_texts:
                        row[h2_title] = "\n".join(section_texts)
                    h2_title = item["text"].replace(" ", "_").lower()
                    section_texts = []
                elif item.get("type") in ["p", "li"]:
                    section_texts.append(item["text"])
                elif "dropdown" in item:
                    acc_title = item["dropdown"].replace(" ", "_").lower()
                    row[f"{h2_title}_{acc_title}" if h2_title else acc_title] = item["content"]

            if h2_title and section_texts:
                row[h2_title] = "\n".join(section_texts)

        all_data.append(row)

driver.quit()

# ---- CREATE DATAFRAME ----
df = pd.DataFrame(all_data)
df.to_csv("pep_pedia_batch.csv", index=False)
print("✅ Batch scraping complete, saved to pep_pedia_batch.csv")
