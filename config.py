import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_CHANNEL_URL = os.getenv("TELEGRAM_CHANNEL_URL", "https://t.me/s/c/3759769266")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "10"))
CHANNEL_ID = "-1003759769266"
