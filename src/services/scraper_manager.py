from multiprocessing import Pool, cpu_count
from typing import List, Callable
from .page_scraper import PageScraper
from ..infrastructure.csv_storage import CSVStorage

def scrape_url_wrapper(url: str):
    scraper = PageScraper()
    return scraper.scrape(url)

class ScraperManager:
    def __init__(self, storage=None, max_processes=None):
        self.storage = storage or CSVStorage()
        self.max_processes = max_processes or min(cpu_count(), 4)

    def run(self, urls: List[str]):
        all_results = []
        error_logs = []

        with Pool(processes=self.max_processes) as pool:
            results = pool.map(scrape_url_wrapper, urls)
            
            for p_data_list, error in results:
                if p_data_list:
                    all_results.extend(p_data_list)
                if error:
                    error_logs.append(error)

        if all_results:
            self.storage.save(all_results)
        
        return error_logs
