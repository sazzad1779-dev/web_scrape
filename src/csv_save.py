
import time
import pandas as pd

all_data = []
expanded = True  # Set to False to only take visible text, True to also include dropdown content
def append_to_csv(results):
    rows = []
    for cat, content in results.items():
        hero = content.get("hero", {})
        row = {"Peptide_Name": hero.get("name", ""),
                "Full_Name": hero.get("subtitle", ""),
                "Method": cat}
        for fact in hero.get("facts", []):
            col_name = fact["label"].replace(" ", "_").lower()
            row[f"{col_name}"] = fact["value"]

        for k, v in content.get("quick_guide", {}).items():
            col_name = k.replace(" ", "_").lower()
            row[f"{col_name}"] = v
        if expanded:
            for section in content.get("sections", []):
                h2_title = None
                section_texts = []

                for item in section:
                    if item.get("type") == "h2":
                        if h2_title and section_texts:
                            row[h2_title] = "\n".join(section_texts)
                        h2_title = item["text"].replace(" ", "_").lower()
                        section_texts = []
                    elif item.get("type") in ["p", "li","table"]:
                        section_texts.append(item["text"])
                    elif "dropdown" in item:
                        acc_title = item["dropdown"].replace(" ", "_").lower()
                        row[f"{h2_title}_{acc_title}" if h2_title else acc_title] = item["content"]

                if h2_title and section_texts:
                    row[h2_title] = "\n".join(section_texts)
        else:
            for section in content.get("sections", []):
                h2_title = None
                section_texts = []

                for item in section:
                    # h2 → column name
                    if item.get("type") == "h2":
                        # Save previous h2 content if exists
                        if h2_title:
                            row[h2_title] = "\n".join(section_texts)
                        h2_title = item["text"].replace(" ", "_").lower()
                        section_texts = []
                    else:
                        # Take text if exists, otherwise content (for dropdowns)
                        text = item.get("text", "")
                        content_val = item.get("content", "")
                        combined = "\n".join([t for t in [text, content_val] if t.strip()])
                        if combined:
                            section_texts.append(combined)

                # Save last h2 section
                if h2_title:
                    row[h2_title] = "\n".join(section_texts)

        # row["scrape_time_seconds"] = round(time.time() - start_time, 2)  # track time
        # print(f"[INFO] Finished {url} in {row['scrape_time_seconds']} seconds")
        # print(f"remaining URLs: {len(URLS) - URLS.index(url) - 1}")
        row["URL"] = content.get("url", "")  # original URL for reference
        rows.append(row)

    return rows, None  # success, no error
