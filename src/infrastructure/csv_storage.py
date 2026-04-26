import pandas as pd
from typing import List
from ..core.models import PeptideData
from ..core.interfaces import IStorage
from ..config import MASTER_CSV

class CSVStorage(IStorage):
    def save(self, data: List[PeptideData]) -> None:
        rows = []
        for p_data in data:
            row = {
                "Peptide_Name": p_data.name,
                "Full_Name": p_data.full_name,
                "Method": p_data.method,
                "URL": p_data.url
            }
            
            # Hero facts
            for fact in p_data.hero.facts:
                col_name = fact.label.replace(" ", "_").lower()
                row[col_name] = f"{fact.value} ({fact.extra})"
            
            # Quick guide
            for k, v in p_data.quick_guide.items():
                col_name = f"quick_guide_{k.replace(' ', '_').lower()}"
                row[col_name] = v
            
            # Community insights
            for k, v in p_data.community_insights.items():
                row[k.replace(" ", "_").lower()] = v
            
            # Poll results
            for k, v in p_data.poll_results.items():
                row[k.replace(" ", "_").lower()] = v
            
            # Sections
            for section in p_data.sections:
                for k, v in section.items():
                    if v:
                        row[k] = v.strip()
            
            rows.append(row)
        
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(MASTER_CSV, index=False)
            print(f"[INFO] Data saved to {MASTER_CSV}")
