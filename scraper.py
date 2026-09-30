import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import datetime
import re

class TelegramChannelScraper:
    def __init__(self, channel_identifier: str):
        """
        :param channel_identifier: Channel username (e.g. 'trading_channel') or full web preview URL
        """
        if channel_identifier.startswith("http://") or channel_identifier.startswith("https://"):
            self.url = channel_identifier
        elif channel_identifier.startswith("@"):
            self.url = f"https://t.me/s/{channel_identifier[1:]}"
        else:
            self.url = f"https://t.me/s/{channel_identifier}"

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def fetch_messages(self, limit: Optional[int] = 20) -> List[Dict[str, Any]]:
        """
        Fetches public messages from Telegram web preview.
        """
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"Error fetching channel data: HTTP status {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "lxml")
            message_elements = soup.find_all("div", class_="tgme_widget_message")

            parsed_messages = []
            for elem in message_elements:
                msg_data = self._parse_message_element(elem)
                if msg_data:
                    parsed_messages.append(msg_data)

            if limit:
                return parsed_messages[-limit:]
            return parsed_messages

        except Exception as e:
            print(f"Exception while scraping Telegram channel: {e}")
            return []

    def _parse_message_element(self, elem) -> Optional[Dict[str, Any]]:
        try:
            # Extract message ID & post link
            msg_id = elem.get("data-post")
            link_elem = elem.find("a", class_="tgme_widget_message_date")
            post_url = link_elem["href"] if link_elem and link_elem.has_attr("href") else ""

            # Extract time
            time_elem = elem.find("time")
            datetime_str = time_elem["datetime"] if time_elem and time_elem.has_attr("datetime") else None

            # Extract text content
            text_elem = elem.find("div", class_="tgme_widget_message_text")
            raw_text = text_elem.get_text("\n", strip=True) if text_elem else ""

            # Extract media/images if present
            image_urls = []
            photo_elems = elem.find_all("a", class_="tgme_widget_message_photo_wrap")
            for photo in photo_elems:
                style = photo.get("style", "")
                match = re.search(r"url\('([^']+)'\)", style)
                if match:
                    image_urls.append(match.group(1))

            # Detect basic Trading Signal patterns (BUY/SELL, Entry, Stop Loss, Take Profit)
            signal_analysis = self._extract_trading_signal(raw_text)

            return {
                "message_id": msg_id,
                "url": post_url,
                "timestamp": datetime_str,
                "text": raw_text,
                "images": image_urls,
                "signal": signal_analysis
            }
        except Exception as e:
            print(f"Error parsing message element: {e}")
            return None

    def _extract_trading_signal(self, text: str) -> Dict[str, Any]:
        """
        Parses trading signals (e.g. BUY / SELL, TP, SL, ENTRY) from message text.
        """
        text_upper = text.upper()
        signal_type = None
        if "BUY" in text_upper or "LONG" in text_upper:
            signal_type = "BUY"
        elif "SELL" in text_upper or "SHORT" in text_upper:
            signal_type = "SELL"

        # Simple regex extractions
        tp_matches = re.findall(r"(?:TP|TAKE PROFIT)\s*[:=]?\s*([\d\.]+)", text_upper)
        sl_matches = re.findall(r"(?:SL|STOP LOSS)\s*[:=]?\s*([\d\.]+)", text_upper)
        entry_matches = re.findall(r"(?:ENTRY|BUY AT|SELL AT)\s*[:=]?\s*([\d\.]+)", text_upper)

        return {
            "is_signal": signal_type is not None or bool(tp_matches or sl_matches),
            "type": signal_type,
            "entry": entry_matches[0] if entry_matches else None,
            "take_profit": tp_matches,
            "stop_loss": sl_matches[0] if sl_matches else None
        }

if __name__ == "__main__":
    # Test execution
    scraper = TelegramChannelScraper("telegram") # Example public channel
    messages = scraper.fetch_messages(limit=5)
    print(f"Scraped {len(messages)} messages.")
    for msg in messages:
        print(f"ID: {msg['message_id']} | Text snippet: {msg['text'][:60]}...")
