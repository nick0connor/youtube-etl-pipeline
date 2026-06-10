import json
import pandas as pd
from pathlib import Path

# This will allegedly work regardless of where script is run from
# parents[0] = readers/, [1] = src/, [2] = project root
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "US_Category_Id.json"

def load_categories(path: Path = DATA_PATH) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
        
    records = [
        {
            "category_id": item["id"],
            "category_name": item["snippet"]["title"],
            "assignable": item["snippet"]["assignable"]
        }
        for item in raw["items"]
    ]
    
    return pd.DataFrame(records)

if __name__ == "__main__": # pragma: no cover
    df = load_categories()
    print(df)