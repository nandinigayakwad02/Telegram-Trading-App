from typing import Dict, Any, List, Optional
from src.signal_parser import SignalParser
from src.pattern_classifier import PatternClassifier
from src.xaus_fetcher import XAUSFetcher

class SignalMatcher:
    """Matches parsed Telegram signals against live/market price data from XAUS."""

    @staticmethod
    def evaluate_signal(raw_text: str, live_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Parses raw text signal, fetches live price if not provided,
        classifies pattern, and calculates P&L.
        """
        parsed = SignalParser.parse_message(raw_text)
        if not parsed or parsed.get("is_standalone_signal"):
            return {"error": "Incomplete or standalone signal format"}

        if live_price is None:
            live_price = XAUSFetcher.get_live_gold_price()

        entry_price = parsed["entry_price"]
        verdict = parsed["recent_verdict"].lower()
        if verdict == "neutral":
            verdict = parsed["overall_signal"].lower()

        pattern_info = PatternClassifier.classify(parsed["digit_code"])

        # Calculate P&L
        price_diff = live_price - entry_price
        price_diff_pct = (price_diff / entry_price) * 100 if entry_price > 0 else 0.0

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
            "timestamp_utc": parsed["timestamp_utc"].strftime("%Y-%m-%d %H:%M:%S") if parsed["timestamp_utc"] else "N/A",
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

    @staticmethod
    def evaluate_batch(signals_list: List[Dict[str, Any]], live_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Evaluates a batch of scraped signals from gold_20m_signals.json.
        """
        if live_price is None:
            live_price = XAUSFetcher.get_live_gold_price()

        results = []
        winning_count = 0
        losing_count = 0
        total_pnl_dollars = 0.0
        pattern_summary = {
            "FULL_HOUSE": {"count": 0, "wins": 0, "losses": 0, "pnl": 0.0, "capital_share": 0.70},
            "SPADES": {"count": 0, "wins": 0, "losses": 0, "pnl": 0.0, "capital_share": 0.15},
            "JACKS": {"count": 0, "wins": 0, "losses": 0, "pnl": 0.0, "capital_share": 0.15}
        }

        for item in signals_list:
            raw_text = item.get("raw_text", "")
            eval_res = SignalMatcher.evaluate_signal(raw_text, live_price=live_price)
            if "error" not in eval_res:
                results.append(eval_res)
                cat = eval_res["pattern_category"]
                pnl = eval_res["pnl_dollars"]
                total_pnl_dollars += pnl

                if cat not in pattern_summary:
                    pattern_summary[cat] = {"count": 0, "wins": 0, "losses": 0, "pnl": 0.0, "capital_share": 0.15}

                pattern_summary[cat]["count"] += 1
                pattern_summary[cat]["pnl"] += pnl

                if eval_res["is_profit"]:
                    winning_count += 1
                    pattern_summary[cat]["wins"] += 1
                elif pnl < 0:
                    losing_count += 1
                    pattern_summary[cat]["losses"] += 1

        total_valid = len(results)
        win_rate = (winning_count / total_valid * 100) if total_valid > 0 else 0.0

        return {
            "total_scraped": len(signals_list),
            "total_valid_signals": total_valid,
            "winning_signals": winning_count,
            "losing_signals": losing_count,
            "win_rate_pct": round(win_rate, 2),
            "total_pnl_dollars": round(total_pnl_dollars, 2),
            "live_price_used": live_price,
            "pattern_summary": pattern_summary,
            "evaluated_signals": results
        }
