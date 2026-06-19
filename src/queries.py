from pathlib import Path
from src.config import get_connection

QUERIES_DIR = Path(__file__).resolve().parents[1] / "queries"

def load_query(name: str) -> str:
    """
    Read a .sql file from queries/ folder by name.
    Ex: load_query("my_query") reads 'queries/my_query.sql'

    Args:
        name: Name of sql file (no extension)

    Returns:
        str: Query command within file
    """
    path = QUERIES_DIR / f"{name}.sql"
    if not path.exists():
        raise FileExistsError(f"No file found at {path}")
    return path.read_text()

def run_query(name: str) -> tuple[list[str], list[tuple]]:
    """
    Loads and executes a named query

    Args:
        name: Name of sql file (no extension)

    Returns:
        tuple: (columns, rows)
    """
    sql = load_query(name)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

    return columns, rows

if __name__ == "__main__":  # pragma: no cover
    cols, rows = run_query("category_breakdown")
    print(cols)
    for row in rows:
        print(row)