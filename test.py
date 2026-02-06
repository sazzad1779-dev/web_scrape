from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException
import time

options = Options()
# if headless:
#     options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")

options.add_argument("--headless")  # runs in background
driver = webdriver.Chrome(options=options)
# url = "https://pep-pedia.org/peptides/5-amino-1mq"
url ="https://pep-pedia.org/peptides/adalank"
# url="https://pep-pedia.org/peptides/omberacetam"
driver.get(url)

wait = WebDriverWait(driver, 5)

def get_category_buttons():
        """Return list of category button texts"""
        try:
            container = driver.find_element(By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10")
            buttons = container.find_elements(By.TAG_NAME, "button")
            categories = [btn.text.strip() for btn in buttons if btn.text.strip()]
            return categories
        except:
            return []
def safe_click(element, retries=3):
        """Click an element safely with scroll and JS fallback"""
        for attempt in range(retries):
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", element)
                element.click()
                return True
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", element)
                return True
            except StaleElementReferenceException:
                time.sleep(0.5)
                continue
        return False
        
categories = get_category_buttons()

for category in categories:
    print(f"\n=== CATEGORY: {category} ===")
    try:
        # Click category
        container = driver.find_element(By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10")
        for btn in container.find_elements(By.TAG_NAME, "button"):
            if btn.text.strip() == category:
                safe_click(btn)
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                break
    except:
        continue
    
    print("\n===== HERO QUICK FACTS =====")
    hero = driver.find_element(By.CSS_SELECTOR, "div.peptide-hero-gradient")

    name = hero.find_element(By.TAG_NAME, "h1").text.strip()
    subtitle = hero.find_element(By.TAG_NAME, "p").text.strip()

    print("Name:", name)
    print("Subtitle:", subtitle)



    cards = hero.find_elements(
        By.XPATH,
        ".//div[contains(@class,'rounded-2xl') and .//div[contains(@class,'font-semibold')]]"
    )

    for card in cards:
        try:
            # Get all visible text lines in order
            lines = [t.strip() for t in card.text.split("\n") if t.strip()]

            if len(lines) < 2:
                continue

            label = lines[0]          # Always first
            main_value = lines[1]     # Always second
            sub_value = lines[2] if len(lines) > 2 else ""

            print(f"▪ {label}: {main_value}" + (f" | {sub_value}" if sub_value else ""))

        except:
            continue




    print("\n===== QUICK START GUIDE =====")

    guide_box = driver.find_element(
        By.XPATH,
        "//h3[contains(text(),'Quick Start Guide')]/ancestor::div[contains(@class,'rounded-xl')]"
    )

    rows = guide_box.find_elements(By.XPATH, ".//div[contains(@class,'flex gap-3')]")

    for row in rows:
        try:
            label = row.find_element(By.XPATH, ".//div[contains(@class,'text-label-sm')]").text.strip()
            value = row.find_element(By.XPATH, ".//div[contains(@class,'text-body-sm')]").text.strip()

            print(f"▪ {label}: {value}")
        except:
            continue

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.mb-12")))

    sections_count = len(driver.find_elements(By.CSS_SELECTOR, "section.mb-12"))
    print("Sections found:", sections_count)

    for i in range(sections_count):
        sections = driver.find_elements(By.CSS_SELECTOR, "section.mb-12")
        section = sections[i]

        print(f"\n====== SECTION {i+1} ======")

        # ---- NORMAL HEADERS & PARAGRAPHS ----
        elements = section.find_elements(By.XPATH, ".//h2 | .//h3 | .//h4 | .//p |.//table| .//li  | .//ol")

        for el in elements:
            # Skip if this element is inside a dropdown button
            if el.find_elements(By.XPATH, "ancestor::div[@role='region']"):
                continue

            tag = el.tag_name.lower()
            text = el.text.strip()
            if text:
                print(f"     ▪ {tag.upper()}: {text}")

        # ---- ACCORDION / DROPDOWN BUTTONS ----
        processed_panels = set()
        buttons = section.find_elements(By.CSS_SELECTOR, 'button[data-state]')

        for btn in buttons:
            try:
                panel_id = btn.get_attribute("aria-controls")
                if panel_id in processed_panels:
                    continue  # avoid duplicates
                processed_panels.add(panel_id)

                title = btn.text.strip()

                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)

                # Click if closed
                if btn.get_attribute("data-state") == "closed":
                    driver.execute_script("arguments[0].click();", btn)

                # Get the panel
                panel = section.find_element(By.ID, panel_id)

                # Wait until panel is rendered (height > 0)
                WebDriverWait(driver, 5).until(
                    lambda d: d.execute_script("return arguments[0].offsetHeight;", panel) > 0
                )

                content = panel.text.strip()

                if title:
                    print(f"\n     🔽 DROPDOWN: {title}")
                if content:
                    print(f"         ▪ {content}")

            except:
                print("     ⚠ Failed to read a dropdown")
                continue
