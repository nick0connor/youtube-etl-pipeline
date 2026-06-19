FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    cron \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

# cron job for daily.py 
# NOTE: Time is in UTC -- 6:00 UTC is 12pm US Eastern, 11am US Central
RUN echo "0 6 * * * cd /app && python daily.py >> /var/log/cron.log 2>&1" > /etc/cron.d/daily-pipeline \
    && chmod 0644 /etc/cron.d/daily-pipeline \
    && crontab /etc/cron.d/daily-pipeline \
    && touch /var/log/cron.log

# Since main.py is for first time use (not for repeated 'on boot' use),
# check a marker file before running command to see if this is initialization.
# Also set cron to run in foreground so docker doesn't auto-close the container.
CMD ["sh", "-c", "test -f /app/.csv_loaded || (python -c 'from src.main import run_csv_pipeline; run_csv_pipeline()' && touch /app/.csv_loaded); cron -f"]