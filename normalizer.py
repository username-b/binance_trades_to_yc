import pandas as pd


class TradesNormalizer:
    """Normalize Binance Vision `trades` rows without aggregating them."""

    COLUMNS = ["trade_id", "price", "qty", "quote_qty", "time", "is_buyer_maker"]
    BINANCE_COLUMNS = ["id", "price", "qty", "quote_qty", "time", "is_buyer_maker"]

    def normalize(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.shape[1] < len(self.COLUMNS):
            raise ValueError(
                f"Trades source has {frame.shape[1]} columns; expected at least {len(self.COLUMNS)}"
            )

        result = frame.iloc[:, : len(self.COLUMNS)].copy()
        normalized_headers = [str(column).strip().lower() for column in result.columns]
        if normalized_headers == self.BINANCE_COLUMNS:
            result.columns = self.COLUMNS
        else:
            # Older Binance archives can have inconsistent/missing header names.
            result.columns = self.COLUMNS

        for column in ("trade_id", "time"):
            result[column] = pd.to_numeric(result[column], errors="coerce")
        for column in ("price", "qty", "quote_qty"):
            result[column] = pd.to_numeric(result[column], errors="coerce")

        maker = result["is_buyer_maker"]
        if maker.dtype != bool:
            result["is_buyer_maker"] = maker.astype(str).str.lower().map(
                {"true": True, "false": False}
            )

        result = result.dropna(subset=self.COLUMNS)
        result["trade_id"] = result["trade_id"].astype("int64")
        result["time"] = result["time"].astype("int64")
        result["price"] = result["price"].astype("float64")
        result["qty"] = result["qty"].astype("float64")
        result["quote_qty"] = result["quote_qty"].astype("float64")
        result["is_buyer_maker"] = result["is_buyer_maker"].astype("bool")
        result["timestamp"] = pd.to_datetime(result["time"], unit="ms", utc=True)

        result = result.drop_duplicates(subset=["trade_id"]).sort_values(
            ["time", "trade_id"]
        )
        return result[
            ["timestamp", "trade_id", "price", "qty", "quote_qty", "time", "is_buyer_maker"]
        ].reset_index(drop=True)
