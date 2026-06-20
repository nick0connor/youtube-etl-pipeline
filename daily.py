import logging
import time
from src.main import run_api_pipeline
from src.summarize import generate_summary
from src.load import load_rejects
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 120 

# Catch 503 errors with retry after delay
def run_summary_with_retry() -> None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            generate_summary()
        except Exception as e:
            log.warning(f"ingest.retry source=daily_summary attempt={attempt}/{MAX_RETRIES} reason={e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
        else:
            return
    
    log.error(f"ingest.error source=daily_summary status=failed_after_retries attempts={MAX_RETRIES}")
    failure_record = pd.DataFrame([{
        "reject_reason": f"AI summary generation failed after {MAX_RETRIES} attempts"
    }])
    load_rejects(failure_record, source_name="daily_summary")

if __name__ == "__main__": # pragma: no cover
    run_api_pipeline()
    run_summary_with_retry()