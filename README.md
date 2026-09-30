# Telegram Trading App - Channel Scraper

A lightweight Python scraper designed to monitor Telegram channel messages and extract trading signals (Buy/Sell, Entry, TP, SL).

## Setup & Installation

1. Navigate to the project directory:
   ```bash
   cd "/home/pc/Documents/Nandini's folder/telegram trading app"
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Telegram channel in `.env`:
   ```env
   # Set username of public channel or public preview URL
   TELEGRAM_CHANNEL_URL=https://t.me/s/YOUR_CHANNEL_USERNAME
   POLL_INTERVAL_SECONDS=10
   ```

4. Run the scraper:
   ```bash
   python main.py
   ```

## Features
- Periodically fetches recent messages without requiring a Telegram user session or bot token for public channels.
- Parses trading signals (`BUY`/`SELL`, `Entry`, `Take Profit`, `Stop Loss`).
- Saves scraped channel history locally in `scraped_telegram_signals.json`.
