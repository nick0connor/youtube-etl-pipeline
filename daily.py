import logging
from src.main import run_api_pipeline
from src.summarize import generate_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

if __name__ == "__main__": # pragma: no cover
    run_api_pipeline()
    generate_summary()