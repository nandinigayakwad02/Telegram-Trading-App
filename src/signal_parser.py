import re
from datetime import datetime
from typing import Dict, Any, Optional

class SignalParser:
    """Parses raw text messages from Telegram signal channels into structured dicts."""

    @staticmethod
    def parse_message(raw_text: str) -> Optional[Dict[str, Any]]:
        """
        Parses a Telegram signal text into structured dictionary.
        Supports format with 'Broker Price:' or 'Price:'.
        """
        try:
            instrument_match = re.search(r'Instrument:\s*([A-Za-z0-9_]+)', raw_text)
            price_match = re.search(r'(?:Broker Price|Price):\s*([\d\.]+)', raw_text)
            time_match = re.search(r'Time:\s*([\d\-\s\:]+)\s*UTC', raw_text)

            phd_match = re.search(r'PHD\s*\(Last 2\):\s*([\d\.]+),\s*([\d\.]+)', raw_text)
            rhd_match = re.search(r'RHD\s*\(Last 2\):\s*([\d\.]+),\s*([\d\.]+)', raw_text)

            buy_match = re.search(r'BUY Total:\s*(\d+),\s*(\d+)', raw_text)
            sell_match = re.search(r'SELL Total:\s*(\d+),\s*(\d+)', raw_text)

            recent_verdict_match = re.search(r'Recent Verdict:\s*(\w+)', raw_text)
            overall_signal_match = re.search(r'OVERALL SIGNAL:\s*(\w+)', raw_text)

            if not (instrument_match and price_match and time_match):
                return None

            instrument = instrument_match.group(1).upper()
            entry_price = float(price_match.group(1))
            utc_time_str = time_match.group(1).strip()
            timestamp_utc = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")

            buy_total = (int(buy_match.group(1)), int(buy_match.group(2))) if buy_match else (0, 0)
            sell_total = (int(sell_match.group(1)), int(sell_match.group(2))) if sell_match else (0, 0)

            recent_verdict = recent_verdict_match.group(1).lower() if recent_verdict_match else "neutral"
            overall_signal = overall_signal_match.group(1).lower() if overall_signal_match else recent_verdict

            # Construct 4-digit code from BUY and SELL totals
            digit_code = f"{buy_total[0]}{buy_total[1]}{sell_total[0]}{sell_total[1]}"

            return {
                "instrument": instrument,
                "entry_price": entry_price,
                "timestamp_utc": timestamp_utc,
                "phd": (float(phd_match.group(1)), float(phd_match.group(2))) if phd_match else (0.0, 0.0),
                "rhd": (float(rhd_match.group(1)), float(rhd_match.group(2))) if rhd_match else (0.0, 0.0),
                "buy_total": buy_total,
                "sell_total": sell_total,
                "digit_code": digit_code,
                "recent_verdict": recent_verdict,
                "overall_signal": overall_signal
            }
        except Exception as e:
            print(f"[SignalParser Error] Failed to parse message: {e}")
            return None
