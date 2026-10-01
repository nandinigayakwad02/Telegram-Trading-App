import asyncio
import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "-1003759769266"))

def parse_trading_signal(text: str, msg_id: int, date_str: str) -> Dict[str, Any]:
    """
    Parses Oanda / Trading signals format from channel messages.
    """
    instrument_match = re.search(r"Instrument:\s*([A-Z0-9_\-]+)", text, re.IGNORECASE)
    price_match = re.search(r"Price:\s*([\d\.]+)", text, re.IGNORECASE)
    time_match = re.search(r"Time:\s*([^\n]+)", text, re.IGNORECASE)
    recent_verdict_match = re.search(r"Recent Verdict:\s*([^\n]+)", text, re.IGNORECASE)
    overall_match = re.search(r"OVERALL SIGNAL[^:]*:\s*([^\n]+)", text, re.IGNORECASE)

    buy_total_match = re.search(r"BUY Total:\s*([^\n]+)", text, re.IGNORECASE)
    sell_total_match = re.search(r"SELL Total:\s*([^\n]+)", text, re.IGNORECASE)

    return {
        "message_id": msg_id,
        "date": date_str,
        "instrument": instrument_match.group(1) if instrument_match else "XAUUSD",
        "price": float(price_match.group(1)) if price_match else None,
        "signal_time": time_match.group(1).strip() if time_match else None,
        "recent_verdict": recent_verdict_match.group(1).strip() if recent_verdict_match else None,
        "overall_signal": overall_match.group(1).strip() if overall_match else None,
        "buy_total": buy_total_match.group(1).strip() if buy_total_match else None,
        "sell_total": sell_total_match.group(1).strip() if sell_total_match else None,
        "raw_text": text
    }

async def fetch_history(days=15, max_limit=3000):
    if not API_ID or not API_HASH:
        print("❌ MISSING TELEGRAM API CREDENTIALS in .env!")
        return

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    print(f"Connecting to Telegram for Private Chat ID: {CHAT_ID}...")
    print(f"Targeting past {days} days of history (Cutoff Date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S UTC')})...")

    api_id_int = int(API_ID)
    async with TelegramClient("session_name", api_id_int, API_HASH) as client:
        entity = await client.get_entity(CHAT_ID)
        title = getattr(entity, 'title', 'Private Channel')
        print(f"Connected to Channel: '{title}'")

        signals: List[Dict[str, Any]] = []
        count = 0

        async for message in client.iter_messages(entity, limit=max_limit):
            if message.date and message.date < cutoff_date:
                print(f"Reached cutoff date {message.date}. Stopping fetch.")
                break

            if message.text:
                count += 1
                signal_data = parse_trading_signal(
                    text=message.text,
                    msg_id=message.id,
                    date_str=str(message.date)
                )
                signals.append(signal_data)

        print(f"\n✅ Successfully fetched {count} signals covering the last {days} days!")
        
        out_file = "gold_20m_signals.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=4, ensure_ascii=False)
            
        print(f"📁 Saved 15-day dataset to: {out_file}\n")

if __name__ == "__main__":
    asyncio.run(fetch_history(days=15, max_limit=3000))
