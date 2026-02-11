# -------------------- IMPORTS -------------------- #
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from src.csv_save import append_to_csv
from src.config import URLS, TIMEOUT, MASTER_CSV, ERROR_LOG, OUTPUT_DIR, create_driver

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

def get_community_insights(driver, wait):
    try:
        card = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h3[contains(text(),'Community Insights')]/ancestor::div[contains(@class,'rounded-xl')]")
        ))
        heading = card.find_element(By.TAG_NAME, "h3").text.strip()
        # Get the responses count
        responses_text = card.find_element(By.XPATH, ".//p[contains(text(),'responses')]").text
        responses = responses_text.split() or "0 responses"

        # Get the insight rows
        rows = card.find_elements(By.CSS_SELECTOR, "div.flex.gap-3.items-start")
        insights = {heading: responses}
        insights.update({
            r.find_element(By.CSS_SELECTOR, ".text-label-sm").text.strip():
            r.find_element(By.CSS_SELECTOR, ".text-body-sm").text.strip()
            for r in rows
        })

        return insights
    except TimeoutException:
        return {}
    
def get_poll_results(driver, wait):
    try:
        card = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h3[contains(text(),'Poll Results')]/ancestor::div[contains(@class,'rounded-xl')]")
        ))
        heading = card.find_element(By.TAG_NAME, "h3").text.strip()
        # Get the responses count
        responses_text = card.find_element(By.XPATH, ".//p[contains(text(),'responses')]").text
        responses = responses_text.split() or "0 responses"

        # Get the insight rows
        rows = card.find_elements(By.CSS_SELECTOR, "div.flex.gap-3.items-start")
        poll_results = {heading: responses}
        poll_results.update({
            r.find_element(By.CSS_SELECTOR, ".text-label-sm").text.strip():
            r.find_element(By.CSS_SELECTOR, ".text-body-sm").text.strip()
            for r in rows
        })

        return poll_results
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

def scrape_url(url):
    driver, wait = create_driver()
    start_time = time.time()
    expanded=True # set to False to only take visible text, True to also capture dropdown content in separate columns
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
            # time.sleep(1)
            # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.peptide-hero-gradient")))

            results[cat] = {
                "hero": get_hero_data(driver, wait),
                "quick_guide": get_quick_guide(driver, wait),
                "community_insights": get_community_insights(driver, wait),
                "poll_results": get_poll_results(driver, wait),
                "sections": get_sections(driver, wait),
                "url": driver.current_url
            }
            
        return append_to_csv(results)  # returns rows, error (None if success)

    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return [], f"{url} - {e}"  # empty rows, log error
    finally:
        driver.quit()
