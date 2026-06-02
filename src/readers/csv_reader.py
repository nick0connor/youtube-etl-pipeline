import pandas as pd
from pathlib import Path

# This will allegedly work regardless of where script is run from
# parents[0] = readers/, [1] = src/, [2] = project root
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "US_Videos.csv"

def load_csv(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(
        path, 
        dtype={
            "video_id": str,
            "category_id": str,
            "comments_disabled": str,
            "ratings_disabled": str,
            "video_error_or_removed": str,
        },
        on_bad_lines="skip"
    )
    return df

if __name__ == "__main__":
    df = load_csv()
    print(df.shape)
    print("\n--- Null counts ---")
    print(df.isnull().sum())

    print("\n--- Sample trending_dates ---")
    print(df["trending_date"].unique()[:10])

    print("\n--- Unique category_ids ---")
    print(sorted(df["category_id"].unique()))
    
    print("\n--- Boolean-ish columns ---")
    print(df["comments_disabled"].unique())
    print(df["ratings_disabled"].unique())
    print(df["video_error_or_removed"].unique())



# Dataset size: (40949, 16) (Rows, Cols)
#
# --- Null counts ---
# video_id                    0
# trending_date               0
# title                       0
# channel_title               0
# category_id                 0
# publish_time                0
# tags                        0
# views                       0
# likes                       0
# dislikes                    0
# comment_count               0
# thumbnail_link              0
# comments_disabled           0
# ratings_disabled            0
# video_error_or_removed      0
# description               570
# dtype: int64
# 
# --- Sample trending_dates --- 
# <StringArray>
# ['17.14.11', '17.15.11', '17.16.11', '17.17.11', '17.18.11', '17.19.11', <---- (YY.DD.MM FORMAT)
#  '17.20.11', '17.21.11', '17.22.11', '17.23.11']
# Length: 10, dtype: str 
# 
# --- Unique category_ids ---
# ['1', '10', '15', '17', '19', '2', '20', '22', '23', '24', '25', '26', '27', '28', '29', '43']
# 
# --- Boolean-ish columns ---
# <StringArray>
# ['False', 'True']
# Length: 2, dtype: str
# <StringArray>
# ['False', 'True']
# Length: 2, dtype: str
# <StringArray>
# ['False', 'True']
# Length: 2, dtype: str