import argparse
import datetime as dt

from dotenv import load_dotenv

from binance_client import BinanceTradesClient
from config_loader import load_config
from normalizer import TradesNormalizer
from pipeline import TradesPipeline
from s3_writer import YandexObjectStorageWriter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download individual Binance Futures trades to Yandex Object Storage"
    )
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def parse_date(value: str | dt.date) -> dt.date:
    return value if isinstance(value, dt.date) else dt.date.fromisoformat(value)


def main() -> None:
    load_dotenv()
    config = load_config(parse_args().config)
    download = config.get("download", {})
    storage = config["storage"]
    sharding = config.get("sharding", {})

    client = BinanceTradesClient(
        base_root=download.get(
            "base_root", "https://data.binance.vision/data/futures/um/daily"
        ),
        timeout=tuple(download.get("timeout", [10, 60])),
        max_retries=int(download.get("retries", 3)),
        backoff=int(download.get("backoff", 2)),
    )
    writer = YandexObjectStorageWriter(
        bucket=storage["bucket"],
        prefix=storage.get("prefix", "raw"),
        overwrite=bool(storage.get("overwrite", False)),
    )
    pipeline = TradesPipeline(client, TradesNormalizer(), writer)

    for symbol in config["symbols"]:
        pipeline.run_range(
            symbol=str(symbol).upper(),
            start_date=parse_date(config["date_range"]["start"]),
            end_date=parse_date(config["date_range"]["end"]),
            shard_id=int(sharding.get("shard_id", 0)),
            shard_total=int(sharding.get("shard_total", 1)),
        )


if __name__ == "__main__":
    main()
