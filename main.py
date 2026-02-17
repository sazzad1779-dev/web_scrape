
import time
import pandas as pd
from multiprocessing import Pool, cpu_count
from src.multi_page_scrape import scrape_url
from src.config import MASTER_CSV, ERROR_LOG
from src.config import URLS

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

    # with Pool(processes=min(cpu_count(), 8)) as pool:
    #     for result in pool.imap_unordered(scrape_url, URLS):
    #         process_result(result)
    with Pool(processes=min(cpu_count(), 4)) as pool:
        results = pool.map(scrape_url, URLS)  # each URL is processed once
        for result in results:
            process_result(result)
    
    # process_result(scrape_url(URLS[0]))
    

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
