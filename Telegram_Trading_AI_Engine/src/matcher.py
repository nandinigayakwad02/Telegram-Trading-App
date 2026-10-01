from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
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

    @staticmethod
    def evaluate_batch_with_15d_candles(signals_list: List[Dict[str, Any]], cache_path: str = "xaus_15d_spot_cache.json") -> Dict[str, Any]:
        """
        Evaluates Telegram signals from gold_20m_signals.json by matching signal timestamps
        against 15 days of cached spot market data candles.
        """
        candles = XAUSFetcher.fetch_and_cache_15d_spot_data(cache_path=cache_path)

        candle_timestamps = []
        for c in candles:
            try:
                dt = datetime.strptime(c["timestamp_utc"], "%Y-%m-%d %H:%M:%S")
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                candle_timestamps.append((dt, c["close"]))
            except Exception:
                pass

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
            parsed = SignalParser.parse_message(raw_text)
            if not parsed or parsed.get("is_standalone_signal"):
                continue

            entry_price = parsed.get("entry_price") or item.get("price")
            verdict = (parsed.get("recent_verdict") or "").lower()
            if verdict == "neutral" or not verdict:
                verdict = (parsed.get("overall_signal") or "").lower()

            if not entry_price or verdict not in ["buy", "sell"]:
                continue

            sig_dt = parsed.get("timestamp_utc")
            if not sig_dt and item.get("date"):
                try:
                    sig_dt = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
                except Exception:
                    pass

            if sig_dt and sig_dt.tzinfo is not None:
                sig_dt = sig_dt.replace(tzinfo=None)

            exit_price = entry_price
            if sig_dt and candle_timestamps:
                target_exit_dt = sig_dt + timedelta(minutes=20)
                closest_candle = min(candle_timestamps, key=lambda c: abs((c[0] - target_exit_dt).total_seconds()))
                if abs((closest_candle[0] - target_exit_dt).total_seconds()) < 7200:
                    exit_price = closest_candle[1]

            pattern_info = PatternClassifier.classify(parsed["digit_code"])

            price_diff = exit_price - entry_price
            price_diff_pct = (price_diff / entry_price) * 100 if entry_price > 0 else 0.0

            if verdict == "buy":
                pnl_dollars = price_diff
                pnl_pct = price_diff_pct
            else:
                pnl_dollars = -price_diff
                pnl_pct = -price_diff_pct

            is_profit = pnl_dollars > 0

            eval_res = {
                "instrument": parsed["instrument"],
                "timestamp_utc": sig_dt.strftime("%Y-%m-%d %H:%M:%S") if sig_dt else "N/A",
                "digit_code": parsed["digit_code"],
                "pattern_category": pattern_info["category"],
                "pattern_emoji": pattern_info["emoji"],
                "capital_share": pattern_info.get("capital_share", 0.15),
                "move_type": pattern_info.get("expected_move", "Standard Move"),
                "verdict": verdict.upper(),
                "entry_price": entry_price,
                "exit_price_20m": exit_price,
                "pnl_dollars": round(pnl_dollars, 2),
                "pnl_pct": round(pnl_pct, 2),
                "is_profit": is_profit
            }

            results.append(eval_res)
            cat = eval_res["pattern_category"]
            pnl = eval_res["pnl_dollars"]
            total_pnl_dollars += pnl

            if cat not in pattern_summary:
                pattern_summary[cat] = {"count": 0, "wins": 0, "losses": 0, "pnl": 0.0, "capital_share": 0.15}

            pattern_summary[cat]["count"] += 1
            pattern_summary[cat]["pnl"] = round(pattern_summary[cat]["pnl"] + pnl, 2)

            if is_profit:
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
            "pattern_summary": pattern_summary,
            "evaluated_signals": results
        }
