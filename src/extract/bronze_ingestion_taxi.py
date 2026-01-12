import os
import yaml
import boto3
import requests
from typing import Optional
from utils.logging_config import log


class BronzeIngestor:
    def __init__(self, source_id: str):
        self.source_id = source_id
        self.config = self._load_config()
        self.s3 = boto3.client(
            "s3", endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
        )
        self.bucket = os.getenv("BRONZE_BUCKET", "silicon-intel-bronze")

    def _load_config(self) -> dict:
        with open("src/config/catalog.yml", "r") as f:
            catalog = yaml.safe_load(f)
            return catalog[self.source_id]

    def run(self):
        # 1. Resolve URL
        source_url: Optional[str] = self.config.get("url")
        if not source_url:
            base = "https://d37ci6vzurychx.cloudfront.net/trip-data"
            # Logic for taxi sources that don't have a hardcoded URL
            source_url = f"{base}/{self.source_id}_tripdata_2024-01.parquet"

        # 2. Resolve S3 Key (Clean wildcards)
        dest_key: str = (
            self.config["source_path"].replace("*", "2024-01").replace("//", "/")
        )

        log.info("ingestion_started", source=self.source_id, url=source_url)

        if isinstance(source_url, str):
            with requests.get(source_url, stream=True) as r:
                r.raise_for_status()
                self.s3.upload_fileobj(r.raw, self.bucket, dest_key)
        else:
            raise ValueError(f"Invalid URL for {self.source_id}")

        log.info("ingestion_success", source=self.source_id, key=dest_key)
