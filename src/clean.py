import pandas as pd
from datetime import datetime
from src.readers.csv_reader import load_csv

def parse_YYDDMM_date(date_str: str) -> datetime | None:
    """
    Parse the date format YY.DD.MM into a proper datetime
    Example: '17.14.11' -> 2017-11-14

    Returns:
        datetime | None: If parse failed
    """
    try:
        year, day, month = date_str.split(".")
        return datetime(int("20"+year), int(month), int(day))
    except Exception:
        return None
    
def cast_booleans(df: pd.DataFrame, bool_cols: list) -> pd.DataFrame:
    """
    Cast string "True"/"False" to columns of actual booleans

    Args:
        df (pd.DataFrame): Original DataFrame
        bool_cols (list): List of columns to modify

    Returns:
        pd.DataFrame: Updated DataFrame
    """
    for col in bool_cols:
        df[col] = df[col].map({ "True": True, "False": False })
    return df

def fill_missing(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """
    Fill non-critical nulls rather than rejecting otherwise valid rows

    Args:
        df (pd.DataFrame): Original DataFrame
        bool_cols (list): List of columns to modify

    Returns:
        pd.DataFrame: Updated DataFrame
    """
    for col in cols:
        df[col] = df[col].fillna("")
    return df

def parse_dates(
    df: pd.DataFrame, 
    str_datetime_cols: list = [],
    YYMMDD_col: str = ""
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parse date columns. Rows that fail to parse are split off as rejects

    Args:
        df (pd.DataFrame): Original DataFrame
        str_datetime_cols (list): Column names where values can be cast via pd.to_datetime
        YYMMDD_col (str): Column where name follows "YY.DD.MM" convention

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (Updated DataFrame, Rejects)
    """
    for col in str_datetime_cols:
        df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    
    if YYMMDD_col != "":
        df[YYMMDD_col] = df[YYMMDD_col].apply(parse_YYDDMM_date)
        
        rejects = df[df[YYMMDD_col].isnull()].copy()
        rejects["reject_reason"] = f"unparseable {YYMMDD_col}"
        
        df = df[df[YYMMDD_col].notnull()].copy()
        return df, rejects
    
    return df, pd.DataFrame()
        
def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main cleaning entry point
    
    Returns:
        (cleaned_df, rejects_df).
    """
    df = fill_missing(df, ["description"])
    df = cast_booleans(df, ["comments_disabled", "ratings_disabled", "video_error_or_removed"])
    df, rejects = parse_dates(df, ["publish_time"], "trending_date")
    
    return df, rejects

if __name__ == "__main__":
    df = load_csv()
    cleaned, rejected = clean(df)
    
    print(f"Clean rows:    {len(cleaned)}")
    print(f"Rejected rows: {len(rejected)}")
    print("\n--- Cleaned dtypes ---")
    print(cleaned.dtypes)
    print("\n--- Sample cleaned row ---")
    print(cleaned.iloc[0][["video_id", "trending_date", "publish_time", "comments_disabled", "category_id"]])