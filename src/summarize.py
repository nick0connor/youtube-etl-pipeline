import logging
from src.config import get_gemini_client
from src.queries import run_query
import textwrap
from src.load import load_summary

log = logging.getLogger(__name__)

# name of file : description for Gemini
QUERIES_FOR_SUMMARY = {
    "live_vs_historical": "CATEGORY COMPARISON (today's % vs historical %)",
    "new_to_trending": "NEW VIDEOS TRENDING TODAY",
    "video_velocity": "FASTEST GROWING VIDEOS (since last snapshot)",
    "engagement_rate": "TOP VIDEOS BY ENGAGEMENT RATE",
}

def format_table(columns: list[str], rows: list[tuple]) -> str:
    """
    Formats tabular data into strings

    Args:
        (columns, rows) from queries.run_query()

    Returns:
        str: Converted table data
    """
    
    if not rows:
        return "No data to report"
    
    lines = [" | ".join(columns)]
    for row in rows:
        lines.append(" | ".join(str(attr) for attr in row))
    return "\n".join(lines)

def gather_report_data() -> dict[str, str]:
    """
    Runs all summary queries and stores formatted results in dict
     
    Returns:
        dict[str, str]: {query_name: formatted_table}
    """
    data = {}
    for name in QUERIES_FOR_SUMMARY.keys():
        columns, rows = run_query(name)
        data[name] = format_table(columns, rows)
    return data

def build_prompt(report_data: dict[str, str], queries_override: dict[str, str] = None) -> str:
    """
    Builds the prompt to pass along to Gemini for plain-English analysis.
    
    Args:
        report_data (dict[str, str]): From gather_data_report()
        queries_override (dict[str, str], optional): Optional replacement for QUERIES_FOR_SUMMARY dict
    
    Returns:
        Full prompt to give to Gemini
    """
    queries_dict = QUERIES_FOR_SUMMARY
    if queries_override:
        queries_dict = queries_override
    
    sections = [
        f"{desc}:\n{report_data[file_name]}" 
        for file_name, desc in queries_dict.items()
    ]
    all_relevant_info = "\n\n".join(sections)
    
    prompt = f"""\
        You are a content analytics assistant. Based on the data below from a
        YouTube trending pipeline, write a short, plain-English daily summary
        (5-7 sentences) for a media team. Cover: whether today's category mix is
        unusual compared to historical norms, what new videos broke into trending,
        which videos are growing fastest, and which videos have the strongest
        audience engagement. Be specific with numbers and titles where useful, but
        keep it readable, not a data dump.

        {all_relevant_info}

        Write the summary now:"""
    
    return textwrap.dedent(prompt)

def generate_summary(queries_override: dict[str, str] = None) -> str:
    report_data = gather_report_data()
    prompt = build_prompt(report_data, queries_override)

    client = get_gemini_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    summary_text = response.text
    load_summary(summary_text)
    log.info("ingest.load source=daily_summaries rows=1")
    
    return summary_text

if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    summary = generate_summary()
    print(summary)