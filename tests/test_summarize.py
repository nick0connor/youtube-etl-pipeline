import pytest
from unittest.mock import MagicMock, patch
from src.summarize import format_table, build_prompt, gather_report_data, generate_summary, QUERIES_FOR_SUMMARY

def test_format_table_with_rows():
    columns = ["title", "views"]
    rows = [("Video A", 1000), ("Video B", 2000)]
    result = format_table(columns, rows)
    assert "title | views" in result
    assert "Video A | 1000" in result
    
def test_format_table_with_no_rows():
    result = format_table(["title", "views"], [])
    assert result == "No data to report"
    
def test_build_prompt_includes_all_sections():
    report_data = {name: f"data for {name}" for name in QUERIES_FOR_SUMMARY}
    prompt = build_prompt(report_data)
    for name in QUERIES_FOR_SUMMARY:
        assert f"data for {name}" in prompt
    assert "Write the summary now" in prompt
    
def test_build_prompt_respects_override():
    override = {"category_breakdown": "CATEGORY BREAKDOWN"}
    report_data = {"category_breakdown": "Gaming | 5"}
    prompt = build_prompt(report_data, queries_override=override)
    assert "CATEGORY BREAKDOWN" in prompt
    assert "Gaming | 5" in prompt
    assert "NEW VIDEOS TRENDING TODAY" not in prompt
    
@patch("src.summarize.run_query")
def test_gather_report_data_calls_run_query_for_each(mock_run_query):
    mock_run_query.return_value = (["col1"], [("val1",)])
    report_data = gather_report_data()
    assert mock_run_query.call_count == len(QUERIES_FOR_SUMMARY)
    assert set(report_data.keys()) == set(QUERIES_FOR_SUMMARY.keys())
    
@patch("src.summarize.load_summary")
@patch("src.summarize.get_gemini_client")
@patch("src.summarize.gather_report_data")
def test_generate_summary_returns_text_and_persists(mock_gather, mock_client, mock_load):
    mock_gather.return_value = {name: "some data" for name in QUERIES_FOR_SUMMARY}
    
    mock_response = MagicMock()
    mock_response.text = "This is a test summary."
    mock_client.return_value.models.generate_content.return_value = mock_response

    result = generate_summary()
    assert result == "This is a test summary."
    mock_load.assert_called_once_with("This is a test summary.")