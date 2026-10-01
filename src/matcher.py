from typing import Dict, Any
from src.signal_parser import SignalParser
from src.pattern_classifier import PatternClassifier
from src.xaus_fetcher import XAUSFetcher

class SignalMatcher:
    """Matches parsed Telegram signals against live market price data from XAUS."""

    @staticmethod
    def evaluate_signal(raw_text: str, live_price: float = None) -> Dict[str, Any]:
        """
        Parses raw text signal, fetches live price if not provided,
        classifies pattern, and calculates P&L.
        """
        parsed = SignalParser.parse_message(raw_text)
        if not parsed:
            return {"error": "Invalid signal format"}

        if live_price is None:
            live_price = XAUSFetcher.get_live_gold_price()

        entry_price = parsed["entry_price"]
        verdict = parsed["recent_verdict"].lower()
        if verdict == "neutral":
            verdict = parsed["overall_signal"].lower()

        pattern_info = PatternClassifier.classify(parsed["digit_code"])

        # Calculate P&L
        price_diff = live_price - entry_price
        price_diff_pct = (price_diff / entry_price) * 100

        if verdict == "buy":
            pnl_dollars = price_diff
            pnl_pct = price_diff_pct
        elif verdict == "sell":
            pnl_dollars = -price_diff
            pnl_pct = -price_diff_pct
        else:
            pnl_dollars = 0.0
            pnl_pct = 0.0

        is_profit = pnl_dollars > 0

        return {
            "instrument": parsed["instrument"],
            "timestamp_utc": parsed["timestamp_utc"],
            "digit_code": parsed["digit_code"],
            "pattern_category": pattern_info["category"],
            "pattern_emoji": pattern_info["emoji"],
            "capital_share": pattern_info["capital_share"],
            "move_type": pattern_info["move_type"],
            "verdict": verdict.upper(),
            "entry_price": entry_price,
            "live_price": live_price,
            "pnl_dollars": round(pnl_dollars, 2),
            "pnl_pct": round(pnl_pct, 2),
            "is_profit": is_profit
        }
