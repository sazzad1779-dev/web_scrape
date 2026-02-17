from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
button_skip_list = [
    "peak",
    "half-life",
    "cleared",
    "hrs",
    "hr",
    "day",
    "24h",
    "7d",
    "14d",
    "30d"
]
# -------------------- CONFIG -------------------- #
TIMEOUT = 5
OUTPUT_DIR = Path("output_v6")
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


def crawl_peptide_urls():
    driver,wait = create_driver()
    driver.get("https://pep-pedia.org/browse")

    time.sleep(5)  # wait for JS to load the peptides

    # Find all peptide links
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/peptides/']")
    peptide_urls = [link.get_attribute("href") for link in links]

    # Remove duplicates
    peptide_urls = list(set(peptide_urls))

    driver.quit()
    
    return peptide_urls
URLS= crawl_peptide_urls()
