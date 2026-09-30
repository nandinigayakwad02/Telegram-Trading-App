import time
import json
import os
from scraper import TelegramChannelScraper
from config import TELEGRAM_CHANNEL_URL, POLL_INTERVAL_SECONDS

DATA_FILE = "scraped_telegram_signals.json"

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_existing_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def main():
    print("=" * 60)
    print("🚀 Telegram Trading App - Channel Scraper Initialized")
    print(f"Target Channel: {TELEGRAM_CHANNEL_URL}")
    print(f"Polling Interval: {POLL_INTERVAL_SECONDS} seconds")
    print("=" * 60)

    scraper = TelegramChannelScraper(TELEGRAM_CHANNEL_URL)
    known_messages = {m["message_id"]: m for m in load_existing_data()}

    while True:
        try:
            print(f"\n[+] Fetching channel messages... ({time.strftime('%Y-%m-%d %H:%M:%S')})")
            messages = scraper.fetch_messages(limit=20)
            
            new_count = 0
            for msg in messages:
                msg_id = msg.get("message_id")
                if msg_id and msg_id not in known_messages:
                    known_messages[msg_id] = msg
                    new_count += 1
                    
                    print(f"\n🔔 NEW MESSAGE RECEIVED [ID: {msg_id}]")
                    print(f"Timestamp: {msg['timestamp']}")
                    print(f"Text: {msg['text']}")
                    
                    if msg["signal"]["is_signal"]:
                        print("📈 [TRADING SIGNAL DETECTED]")
                        print(f"   Type: {msg['signal']['type']}")
                        print(f"   Entry: {msg['signal']['entry']}")
                        print(f"   Take Profit: {msg['signal']['take_profit']}")
                        print(f"   Stop Loss: {msg['signal']['stop_loss']}")

            if new_count > 0:
                save_data(list(known_messages.values()))
                print(f"✅ Saved {new_count} new messages to {DATA_FILE}")
            else:
                print("ℹ️ No new messages found.")

        except KeyboardInterrupt:
            print("\nStopping Telegram Trading App Scraper.")
            break
        except Exception as e:
            print(f"⚠️ Error during poll cycle: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
