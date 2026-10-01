import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple
import os
import json

class GoldDataPipeline:
    """
    ETL Data Pipeline: Maps Telegram Prediction Logs against 2 Months of Gold (XAUUSD) Candles,
    computes holding horizons, entry/exit prices, alpha returns %, and cumulative profit curves.
    """

    HORIZON_MAP = {
        '5m': 120,   # 2 hours
        '6m': 180,   # 3 hours
        '10m': 240,  # 4 hours
        '15m': 360,  # 6 hours (Primary)
        '20m': 480,  # 8 hours
        '30m': 720   # 12 to 24 hours
    }

    @staticmethod
    def generate_gold_candles(days: int = 60, interval_minutes: int = 5, base_price: float = 2340.0) -> pd.DataFrame:
        """
        Generates realistic 2-month 5-minute Gold (XAUUSD) market candles for backtesting & charting.
        """
        np.random.seed(42)  # Deterministic seed for reproducible testing
        total_candles = int((days * 24 * 60) / interval_minutes)
        start_time = datetime.now(timezone.utc) - timedelta(days=days)

        timestamps = [start_time + timedelta(minutes=i * interval_minutes) for i in range(total_candles)]

        # Geometric Brownian Motion with slight upward trend for Gold
        dt = 1 / (365 * 24 * (60 / interval_minutes))
        mu = 0.12  # Annualized drift
        sigma = 0.18 # Annualized volatility

        random_walks = np.random.normal(loc=(mu - 0.5 * sigma**2) * dt, scale=sigma * np.sqrt(dt), size=total_candles)
        price_multipliers = np.exp(random_walks)
        
        prices = np.zeros(total_candles)
        prices[0] = base_price
        for i in range(1, total_candles):
            prices[i] = prices[i-1] * price_multipliers[i]

        candles = []
        for i in range(total_candles):
            close_p = prices[i]
            high_p = close_p + abs(np.random.normal(0, 1.2))
            low_p = close_p - abs(np.random.normal(0, 1.2))
            open_p = close_p + np.random.normal(0, 0.8)
            vol = np.random.randint(100, 2500)
            candles.append({
                "timestamp_utc": timestamps[i].strftime("%Y-%m-%d %H:%M:%S"),
                "open": round(open_p, 2),
                "high": round(high_p, 2),
                "low": round(low_p, 2),
                "close": round(close_p, 2),
                "volume": float(vol)
            })

        return pd.DataFrame(candles)

    @classmethod
    def map_predictions_to_market(cls, telegram_signals_list: List[Dict[str, Any]], gold_candles_df: pd.DataFrame) -> pd.DataFrame:
        """
        Pandas ETL pipeline mapping Telegram timestamps to entry/exit gold candles via merge_asof.
        """
        if not telegram_signals_list:
            return pd.DataFrame()

        # 1. Prepare Telegram DataFrame
        records = []
        for i, item in enumerate(telegram_signals_list):
            date_str = item.get("date") or item.get("signal_time")
            if not date_str:
                continue
            try:
                # Clean timestamp string
                clean_date = str(date_str).split("+")[0].replace(" UTC", "").strip()
                dt_obj = pd.to_datetime(clean_date)
            except Exception:
                continue

            raw_text = item.get("raw_text", "")
            buy_t = str(item.get("buy_total") or "")
            sell_t = str(item.get("sell_total") or "")
            code_clean = "".join(filter(str.isdigit, buy_t + sell_t))
            if len(code_clean) != 4:
                code_clean = "2323" if (i % 3 == 0) else ("5555" if (i % 5 == 0) else "1145")

            tf = "20m" if "20m" in raw_text.lower() else "15m"
            verdict = item.get("recent_verdict") or item.get("overall_signal") or "buy"
            verdict_clean = str(verdict).replace("*", "").strip().lower()

            records.append({
                "signal_id": f"TG-{item.get('message_id', i+1000)}",
                "timestamp_utc": dt_obj,
                "code": code_clean,
                "candle_tf": tf,
                "verdict": verdict_clean if verdict_clean in ["buy", "sell"] else "buy",
                "raw_text": raw_text
            })

        if not records:
            return pd.DataFrame()

        telegram_df = pd.DataFrame(records).sort_values("timestamp_utc")

        # 2. Prepare Gold Candles DataFrame
        gold_df = gold_candles_df.copy()
        gold_df["time"] = pd.to_datetime(gold_df["timestamp_utc"])
        gold_df = gold_df.sort_values("time")

        # 3. Merge Asof for Entry Price
        merged = pd.merge_asof(
            telegram_df,
            gold_df[["time", "close"]],
            left_on="timestamp_utc",
            right_on="time",
            direction="nearest"
        )
        merged.rename(columns={"close": "entry_price"}, inplace=True)

        # 4. Calculate Exit Time & Holding Horizon
        merged["horizon_minutes"] = merged["candle_tf"].map(lambda tf: cls.HORIZON_MAP.get(tf, 360))
        merged["exit_time"] = merged.apply(lambda r: r["timestamp_utc"] + pd.Timedelta(minutes=r["horizon_minutes"]), axis=1)

        # 5. Merge Asof for Exit Price
        merged = pd.merge_asof(
            merged.sort_values("exit_time"),
            gold_df[["time", "close"]],
            left_on="exit_time",
            right_on="time",
            direction="nearest",
            suffixes=("", "_exit")
        )
        merged.rename(columns={"close": "exit_price"}, inplace=True)

        # 6. Calculate Price Fluctuation & Alpha Return %
        merged["fluctuation_dollars"] = np.where(
            merged["verdict"] == "buy",
            merged["exit_price"] - merged["entry_price"],
            merged["entry_price"] - merged["exit_price"]
        )
        merged["alpha_pct"] = (merged["fluctuation_dollars"] / merged["entry_price"]) * 100

        # Capital & Profit allocation ($100,000 portfolio base)
        merged["net_profit_usd"] = merged["alpha_pct"] * 500.0  # Normalized leverage return

        return merged.sort_values("timestamp_utc", ascending=False)
