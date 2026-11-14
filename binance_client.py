import io
import time
import zipfile
from typing import Optional

import pandas as pd
import requests


class BinanceTradesClient:
    """Download individual USD-M Futures trades from Binance Vision."""

    SOURCE = "trades"

    def __init__(
        self,
        base_root: str,
        timeout: tuple[int, int] = (10, 60),
        max_retries: int = 3,
        backoff: int = 2,
    ) -> None:
        self.base_root = base_root.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff

    def build_url(self, symbol: str, date: str) -> str:
        return (
            f"{self.base_root}/{self.SOURCE}/{symbol}/"
            f"{symbol}-{self.SOURCE}-{date}.zip"
        )

    def download_zip(self, url: str) -> Optional[bytes]:
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    return response.content
                if response.status_code == 404:
                    return None
                response.raise_for_status()
            except requests.RequestException:
                if attempt == self.max_retries:
                    raise
                time.sleep(self.backoff ** attempt)
        return None

    @staticmethod
    def unzip_to_frame(content: bytes) -> pd.DataFrame:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if len(csv_names) != 1:
                raise ValueError(f"Expected one CSV in archive, found {len(csv_names)}")
            with archive.open(csv_names[0]) as stream:
                return pd.read_csv(stream, low_memory=False).dropna(how="all")

    def load_day(self, symbol: str, date: str) -> Optional[pd.DataFrame]:
        content = self.download_zip(self.build_url(symbol, date))
        return None if content is None else self.unzip_to_frame(content)
