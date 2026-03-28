from __future__ import annotations

import requests

from scanner.config import TelegramConfig


class TelegramNotifier:
    def __init__(self, config: TelegramConfig) -> None:
        self.config = config

    def send_signal(self, signal: str, symbol: str, price: float) -> None:
        emoji = "🚀" if signal == "BUY" else "🔻"
        message = f"{emoji} {signal} SIGNAL: {symbol} @ {price:.2f}"
        url = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"

        response = requests.post(
            url,
            json={"chat_id": self.config.chat_id, "text": message},
            timeout=15,
        )
        response.raise_for_status()
