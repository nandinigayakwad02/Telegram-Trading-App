import json
import os
from src.xaus_fetcher import XAUSFetcher
from src.matcher import SignalMatcher

def run_test():
    print("=" * 60)
    print("🧪 Testing 15-Day Spot Market Data Fetching & Signal Matching")
    print("=" * 60)

    # 1. Fetch & Cache 15-day spot market candles
    candles = XAUSFetcher.fetch_and_cache_15d_spot_data(cache_path="xaus_15d_spot_cache.json")
    print(f"📊 Loaded {len(candles)} 15-day spot market candles.")

    # 2. Load signals from gold_20m_signals.json
    signals_path = "../gold_20m_signals.json"
    if not os.path.exists(signals_path):
        signals_path = "gold_20m_signals.json"

    with open(signals_path, "r", encoding="utf-8") as f:
        signals_list = json.load(f)

    print(f"📩 Loaded {len(signals_list)} raw Telegram signals.")

    # 3. Evaluate signals against 15-day cached candles
    report = SignalMatcher.evaluate_batch_with_15d_candles(signals_list, cache_path="xaus_15d_spot_cache.json")

    print("\n📈 EVALUATION RESULTS:")
    print(f"   • Total Scraped: {report['total_scraped']}")
    print(f"   • Total Valid Signals: {report['total_valid_signals']}")
    print(f"   • Winning Signals: {report['winning_signals']}")
    print(f"   • Losing Signals: {report['losing_signals']}")
    print(f"   • Win Rate: {report['win_rate_pct']}%")
    print(f"   • Total PnL: ${report['total_pnl_dollars']}")

    # Save evaluated report
    report_path = "evaluated_signals_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print(f"\n💾 Saved evaluated signals report to '{report_path}'.")
    print("✅ TEST COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_test()
