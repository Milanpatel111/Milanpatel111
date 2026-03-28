# Live Stock Market Scanner with Telegram Alerts

A modular Python scanner that:
- logs into SmartAPI (Angel One) or Upstox,
- pulls live/intraday market data for multiple stocks,
- applies breakout + volume spike (+ optional VWAP filter) logic,
- sends BUY/SELL alerts to Telegram,
- stores signals in CSV logs.

## 1) Strategy Rules

For each symbol, scanner evaluates:
1. **Breakout/Breadkown**
   - BUY when `LTP > opening candle high`
   - SELL when `LTP < opening candle low`
2. **Volume spike**
   - current candle volume > previous candle volume
3. **Optional VWAP filter** (`use_vwap_filter: true`)
   - BUY only if `LTP > VWAP`
   - SELL only if `LTP < VWAP`

Duplicate same-direction alerts per symbol are blocked.

---

## 2) Project Structure

```text
.
├── main.py
├── bot.py
├── config.json
├── .env.example
├── requirements.txt
└── scanner/
    ├── config.py
    ├── models.py
    ├── notifier.py
    ├── scanner.py
    ├── signal_logger.py
    ├── strategy.py
    └── brokers/
        ├── base.py
        ├── smartapi.py
        └── upstox.py
```

---

## 3) Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

## 4) Environment Variables

Copy the example and fill credentials:

```bash
cp .env.example .env
```

Required values:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- For SmartAPI:
  - `SMARTAPI_API_KEY`
  - `SMARTAPI_CLIENT_ID`
  - `SMARTAPI_PASSWORD`
  - `SMARTAPI_TOTP_SECRET`
- For Upstox (if broker is `upstox`):
  - `UPSTOX_ACCESS_TOKEN`

## 5) Configure Symbols and Strategy

Edit `config.json`:

- `broker`: `smartapi` or `upstox`
- `scan_interval_seconds`: scanner loop interval (5–10s recommended)
- `timeframe_minutes`: candle timeframe used for volume/opening levels
- `use_vwap_filter`: true/false
- `symbols`: list of symbols with `symbol`, `exchange`, `token`
- `log_file`: output CSV path for signal logs

> For SmartAPI, ensure each symbol has the correct **exchange token**.

## 6) Run Scanner

```bash
python main.py
```

(or `python bot.py`, which maps to `main.py`)

You should see logs like:
- `BUY SIGNAL: RELIANCE-EQ @ 2987.40`
- `Duplicate signal skipped for RELIANCE-EQ (BUY)`

## 7) Telegram Alert Format

- `🚀 BUY SIGNAL: SYMBOL @ PRICE`
- `🔻 SELL SIGNAL: SYMBOL @ PRICE`

## 8) Output Logging

Signals are persisted in CSV:

```csv
timestamp,symbol,signal,price
2026-03-28T10:00:01.123456,RELIANCE-EQ,BUY,2987.40
```

## 9) Error Handling Included

- API/login failures raise and are logged.
- Scanner loop catches exceptions and continues running.
- SmartAPI session is validated and token refresh is attempted.

## 10) Bonus Notes (Multi-broker support)

- **SmartAPI**: full login via API key/client/password/TOTP.
- **Upstox**: access-token based mode (set `UPSTOX_ACCESS_TOKEN`).

If you want, next step can be adding:
- dynamic strategy config (JSON-based rule toggles),
- market-hours guard,
- async batching/WebSocket feed for faster scans.
