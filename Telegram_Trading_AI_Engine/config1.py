"""
Configuration settings for Telegram Trading Signal Matcher & XAUS API
"""

# XAUS API Config (xaus.com)
XAUS_API_BASE_URL = "https://xaus.com/api"
XAUS_LIVE_PRICE_URL = "https://xaus.com/api/gold-price"
XAUS_HISTORICAL_URL = "https://xaus.com/api/historical"

# Trading Instrument Defaults
DEFAULT_SYMBOL = "XAUUSD"

# Card Pattern Capital Allocation Rules
PATTERN_ALLOCATION = {
    "FULL_HOUSE": {"capital_share": 0.70, "move_type": "Big Persistent Move (12-24 hrs)"},
    "SPADES": {"capital_share": 0.15, "move_type": "Continuous Trend Move"},
    "JACKS": {"capital_share": 0.15, "move_type": "Medium Move"}
}

# Target Performance Settings
TARGET_DAILY_RETURN = 0.0020  # 0.20% per day
MIN_WIN_RATE_THRESHOLD = 0.60 # 60% win rate to include in dashboard
