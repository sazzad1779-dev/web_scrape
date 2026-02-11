import time
import pandas as pd

all_data = []
expanded = True  # Set to False to only take visible text, True to also include dropdown content

def append_to_csv(results):
    rows = []
    for cat, content in results.items():
        hero = content.get("hero", {})
        row = {
            "Peptide_Name": hero.get("name", ""),
            "Full_Name": hero.get("subtitle", ""),
            "Method": cat
        }
        
        # Add facts
        for fact in hero.get("facts", []):
            col_name = fact["label"].replace(" ", "_").lower()
            row[f"{col_name}"] = fact["value"]

        # Add quick guide
        for k, v in content.get("quick_guide", {}).items():
            col_name = k.replace(" ", "_").lower()
            row[f"quick_guide_{col_name}"] = v
        
        # Process sections
        if expanded:
            for section in content.get("sections", []):
                h2_title = None
                section_texts = []

                for item in section:
                    # Handle h2 headers
                    if item.get("type") == "h2":
                        if h2_title and section_texts:
                            row[h2_title] = "\n".join(section_texts)
                        h2_title = item["text"].replace(" ", "_").lower()
                        section_texts = []
                    
                    # Handle static content (p, li, table)
                    elif item.get("type") in ["p", "li", "table","h3","h4"]:
                        section_texts.append(item["text"])
                    
                    # Handle accordion dropdowns
                    elif "dropdown" in item:
                        acc_title = item["dropdown"].replace(" ", "_").lower()
                        col_key = f"{h2_title}_{acc_title}" if h2_title else acc_title
                        row[col_key] = item["content"]
                    
                    # Handle tab buttons
                    elif "tab" in item:
                        tab_title = item["tab"].replace(" ", "_").lower()
                        col_key = f"{h2_title}_{tab_title}" if h2_title else tab_title
                        row[col_key] = item["content"]

                # Save remaining h2 content
                if h2_title and section_texts:
                    row[h2_title] = "\n".join(section_texts)
        
        else:
            for section in content.get("sections", []):
                h2_title = None
                section_texts = []

                for item in section:
                    # h2 → column name
                    if item.get("type") == "h2":
                        if h2_title and section_texts:
                            row[h2_title] = "\n".join(section_texts)
                        h2_title = item["text"].replace(" ", "_").lower()
                        section_texts = []
                    else:
                        # Collect all text/content regardless of type
                        text = item.get("text", "")
                        content_val = item.get("content", "")
                        combined = "\n".join([t for t in [text, content_val] if t.strip()])
                        if combined:
                            section_texts.append(combined)

                # Save last h2 section
                if h2_title and section_texts:
                    row[h2_title] = "\n".join(section_texts)
        for key,value in content.get("community_insights", {}).items():
            if value.strip():
                row[key.replace(" ", "_").lower()] = value
        for key,value in content.get("poll_results", {}).items():
            
                row[key.replace(" ", "_").lower()] = value
            
        row["URL"] = content.get("url", "")
        rows.append(row)

    return rows, None  # success, no error