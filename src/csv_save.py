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
            row[f"{col_name}"] = f'{fact["value"]} ({fact["extra"]}) '

        # Add quick guide
        for k, v in content.get("quick_guide", {}).items():
            col_name = k.replace(" ", "_").lower()
            row[f"quick_guide_{col_name}"] = v
        
        # Process sections
        if expanded:
            for section in content.get("sections", []):
                for key, value in section.items():
                    if value:  # avoid empty values
                        row[key] = value.strip()   
        
        for key,value in content.get("community_insights", {}).items():
            if value.strip():
                row[key.replace(" ", "_").lower()] = value
        for key,value in content.get("poll_results", {}).items():
            
                row[key.replace(" ", "_").lower()] = value
            
        row["URL"] = content.get("url", "")
        rows.append(row)

    return rows, None  # success, no error