from src.crawl_url import crawl_peptide_urls
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# -------------------- CONFIG -------------------- #
URLS = crawl_peptide_urls()
TIMEOUT = 5
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
MASTER_CSV = OUTPUT_DIR / "pep_pedia_master.csv"
ERROR_LOG = OUTPUT_DIR / "error_log.txt"
button_skip_list = ["Peak: 2 hrs", "Half-life: 2 hrs", "Cleared: ~10 hrs", "Peak", "Half-life", "24h", "7d","14d","30d"]
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