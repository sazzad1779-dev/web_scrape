from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time

# -------------------- CONFIG -------------------- #
TIMEOUT = 5
OUTPUT_DIR = Path("output_v6")
OUTPUT_DIR.mkdir(exist_ok=True)
MASTER_CSV = OUTPUT_DIR / "pep_pedia_master.csv"
ERROR_LOG = OUTPUT_DIR / "error_log.txt"

button_skip_list = [
    "peak", "half-life", "cleared", "hrs", "hr", "day", "24h", "7d", "14d", "30d"
]

def crawl_peptide_urls():
    from .infrastructure.webdriver_factory import WebDriverFactory
    driver, wait = WebDriverFactory.create_driver()
    try:
        driver.get("https://pep-pedia.org/browse")
        time.sleep(5)  # wait for JS to load the peptides
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/peptides/']")
        peptide_urls = [link.get_attribute("href") for link in links]
        return list(set(peptide_urls))
    finally:
        driver.quit()
