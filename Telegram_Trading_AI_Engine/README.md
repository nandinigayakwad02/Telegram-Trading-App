# 🚀 Telegram Trading Signal Matcher & XAUS API Integration

System for parsing Telegram intraday trading signals, classifying 4-digit card patterns (Full House 🏠, Spades ♠️, One-Eye Jacks 🃏), and matching them with live & historical market data from **XAUS API (xaus.com)** to calculate real-time P&L.

---

## 📁 Project Structure

```
Telegram Trading/
├── config.py                 # System configuration & risk parameters
├── main.py                   # Main entry point & demo runner
├── requirements.txt          # Required Python dependencies
├── README.md                 # Documentation
└── src/                      # Source modules
    ├── __init__.py           # Package marker
    ├── signal_parser.py      # Telegram message text regex parser
    ├── pattern_classifier.py # Card pattern classifier (Full House / Spades / Jacks)
    ├── xaus_fetcher.py       # XAUS API live market price fetcher
    └── matcher.py            # Signal vs Live Market Price P&L calculator
```

---

## 🛠️ Installation & Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the system:
   ```bash
   python main.py
   ```

---

## 🃏 Pattern Rules & Capital Allocation

| Pattern | Code Rules | Move Expected | Capital Share |
|---|---|---|---|
| **Full House 🏠** | Quad digits (`5555`) or alternating (`2323`) | 12-24 hr Big Persistent Move | **70%** |
| **Spades ♠️** | 2-and-2 split (`1145`, `5522`) | Continuous Trend Move | **15%** |
| **One-Eye Jacks 🃏** | 3-and-1 split (`5551`, `1115`) | Medium Move | **15%** |
