
import pandas as pd

all_data = []
def append_to_csv(results):
    for cat, content in results.items():
        row = {"category": cat, "url": content.get("url", "")}
        # ---- HERO ----
        hero = content.get("hero", {})
        row["name"] = hero.get("name", "")
        row["subtitle"] = hero.get("subtitle", "")
        
        # Add facts as separate columns (label as column name, value as column value)
        for fact in hero.get("facts", []):
            col_name = fact["label"].replace(" ", "_").lower()
            row[f"{col_name}"] = fact["value"]

        # ---- QUICK GUIDE ----
        quick_guide = content.get("quick_guide", {})
        for k, v in quick_guide.items():
            col_name = k.replace(" ", "_").lower()
            row[f"{col_name}"] = v

        # ---- SECTIONS ----
        sections = content.get("sections", [])
        for section in sections:
            h2_title = None
            section_texts = []

            for item in section:
                if item.get("type") == "h2":
                    h2_title = item["text"].replace(" ", "_").lower()
                    section_texts = []
                elif item.get("type") in ["p", "li"]:
                    section_texts.append(item["text"])
                elif "dropdown" in item:
                    # If accordion content
                    acc_title = item["dropdown"].replace(" ", "_").lower()
                    row[f"{h2_title}_{acc_title}" if h2_title else acc_title] = item["content"]

            if h2_title and section_texts:
                row[h2_title] = " | ".join(section_texts)

        all_data.append(row)
    return all_data