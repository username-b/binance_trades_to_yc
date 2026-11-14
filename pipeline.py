import datetime as dt

from binance_client import BinanceTradesClient
from normalizer import TradesNormalizer
from s3_writer import YandexObjectStorageWriter


class TradesPipeline:
    def __init__(
        self,
        client: BinanceTradesClient,
        normalizer: TradesNormalizer,
        writer: YandexObjectStorageWriter,
    ) -> None:
        self.client = client
        self.normalizer = normalizer
        self.writer = writer

    def run_range(
        self,
        symbol: str,
        start_date: dt.date,
        end_date: dt.date,
        shard_id: int = 0,
        shard_total: int = 1,
    ) -> None:
        if end_date < start_date:
            raise ValueError("date_range.end must not be earlier than date_range.start")
        if shard_total < 1 or not 0 <= shard_id < shard_total:
            raise ValueError("shard_id must be in range [0, shard_total)")

        day_count = (end_date - start_date).days + 1
        dates = [start_date + dt.timedelta(days=offset) for offset in range(day_count)]
        dates = [date for index, date in enumerate(dates) if index % shard_total == shard_id]
        print(f"{symbol}: shard {shard_id}/{shard_total}, {len(dates)} days")

        for date in dates:
            date_string = date.isoformat()
            try:
                frame = self.client.load_day(symbol, date_string)
                if frame is None or frame.empty:
                    print(f"No data: {symbol} {date_string}")
                    continue
                self.writer.write(self.normalizer.normalize(frame), symbol, date_string)
            except Exception as error:
                print(f"ERROR {symbol} {date_string}: {error}")
