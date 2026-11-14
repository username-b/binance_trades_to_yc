import io
import os

import boto3
import pandas as pd
from botocore.exceptions import ClientError


class YandexObjectStorageWriter:
    def __init__(self, bucket: str, prefix: str = "", overwrite: bool = False) -> None:
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        self.overwrite = overwrite
        self.s3 = boto3.client(
            "s3",
            endpoint_url=os.environ.get("YC_ENDPOINT", "https://storage.yandexcloud.net"),
            region_name=os.environ.get("YC_REGION", "ru-central1"),
            aws_access_key_id=os.environ.get("YC_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("YC_SECRET_ACCESS_KEY"),
        )

    def build_key(self, symbol: str, date: str) -> str:
        parts = [self.prefix, "trades", f"symbol={symbol}", f"date={date}", "data.parquet"]
        return "/".join(part for part in parts if part)

    def exists(self, key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as error:
            code = str(error.response.get("Error", {}).get("Code", ""))
            if code in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise

    def write(self, frame: pd.DataFrame, symbol: str, date: str) -> bool:
        key = self.build_key(symbol, date)
        if not self.overwrite and self.exists(key):
            print(f"Skip exists: s3://{self.bucket}/{key}")
            return False

        buffer = io.BytesIO()
        frame.to_parquet(buffer, index=False, engine="pyarrow", compression="zstd")
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=buffer.getvalue(),
            ContentType="application/vnd.apache.parquet",
        )
        print(f"Uploaded {len(frame)} trades: s3://{self.bucket}/{key}")
        return True
