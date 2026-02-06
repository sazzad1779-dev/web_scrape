

# PepPedia Scraper

A Python project to **scrape peptide data from PepPedia** using Selenium.
Supports **single URL scraping** or **batch/multiprocessing scraping**.

---

## Features

* Scrape **hero information** (`name`, `subtitle`, `facts`)
* Scrape **Quick Start Guide**
* Scrape **sections** with multiple paragraphs and accordions
* Supports **single URL scraping**
* Supports **multiple URLs scraping with multiprocessing**
* Outputs results to **CSV** ready for analysis or RAG/LLM ingestion

---

## Requirements

* Python 3.10+
* Google Chrome installed
* ChromeDriver matching your Chrome version
* `uv` Python package manager installed

---

## Installation

1. **Clone the repository**:

```bash
git clone <repo-url>
cd <project-folder>
```

2. **Install dependencies using `uv`**:

```bash
uv sync
```

3. **Download ChromeDriver** matching your Chrome version and add it to your PATH:

* [ChromeDriver Download](https://sites.google.com/chromium.org/driver/)

---

## File Structure

```
src/
├── single_page_scrape.py   # Scrapes a single URL
├── multi_scrape.py         # Scrapes multiple URLs using multiprocessing
```

---

## Configuration

* **Single URL**: Edit `single_page_scrape.py` to set the `URL` variable:

```python
URL = "https://pep-pedia.org/peptides/adalank"
```

* **Multiple URLs**: Edit `multi_scrape.py` and update the `URLS` list:

```python
URLS = [
    "https://pep-pedia.org/peptides/adalank",
    "https://pep-pedia.org/peptides/5-amino-1mq",
    # Add more URLs here
]
```

---

## Running the Scraper

### Single URL Scrape

```bash
uv run -m src.single_page_scrape
```

* Scrapes the single URL specified in `single_page_scrape.py`.
* Output CSV: `pep_pedia_single.csv`

### Multiple URLs Scrape

```bash
uv run -m src.multi_page_scrape
```

* Scrapes all URLs in the `URLS` list with **multiprocessing**.
* Output CSV: `pep_pedia_batch_multiprocess.csv`

---

## Notes

* Each Selenium process opens its **own Chrome instance**, so **multiprocessing consumes more memory**.
* Make sure **ChromeDriver version matches your installed Chrome**.
* The scraper handles:

  * Multiple categories per peptide
  * Hero section
  * Quick Start Guide
  * Sections and accordions with multiple paragraphs (using newlines)
* For large batches, adjust `max_workers` in `multi_scrape.py` to match your system resources.
