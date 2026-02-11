from src.config import URLS, TIMEOUT, MASTER_CSV, ERROR_LOG, OUTPUT_DIR, create_driver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
driver, wait = create_driver()

url ="https://pep-pedia.org/peptides/adalank"
driver.get(url)
# time.sleep(2)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10")))
result =driver.find_elements(By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10 button")

print([b.text.strip() for b in result if b.text.strip()])