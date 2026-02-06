from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
TIMEOUT = 8

def crawl_peptide_urls():
    # Setup Chrome
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, TIMEOUT)
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://pep-pedia.org/browse")

    time.sleep(5)  # wait for JS to load the peptides

    # Find all peptide links
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/peptides/']")
    peptide_urls = [link.get_attribute("href") for link in links]

    # Remove duplicates
    peptide_urls = list(set(peptide_urls))

    driver.quit()
    
    return peptide_urls
