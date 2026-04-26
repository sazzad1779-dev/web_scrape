import time
from src.config import crawl_peptide_urls, ERROR_LOG
from src.services.scraper_manager import ScraperManager

if __name__ == "__main__":
    start_total = time.time()
    
    print("[INFO] Crawling peptide URLs...")
    urls = crawl_peptide_urls()
    print(f"[INFO] Found {len(urls)} URLs to scrape.")

    # Instantiate manager and run
    manager = ScraperManager()
    error_logs = manager.run(urls)

    # Save error log
    if error_logs:
        with open(ERROR_LOG, "w") as f:
            for line in error_logs:
                f.write(line + "\n")
        print(f"[INFO] Errors logged at {ERROR_LOG}")

    print(f"[INFO] Total scraping time: {round(time.time() - start_total, 2)} seconds")
