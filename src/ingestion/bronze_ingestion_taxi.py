# bronze_ingestion_taxi.py
import os
import yaml
import boto3
import requests
from typing import Optional
from utils.logging_config import log
from abc import ABC, abstractmethod

# TODO: WEZTERM: 'tmux-session save' in wezterm! avoiding closing all the dev env unnecesarily
# TODO: creat a NAMING CONVENTION for aws secrets
# TODO: the bronze & siver Classes should have the ObservabilityManager embedded/implemented
# NOTE: the IAM provide is implicit, boto.client gets it at background
# NOTE: However the 'aws secrets' is not, it requires call a boto.client method


# Base Contract
class BaseIngestor(ABC):
    @abstractmethod
    def ingest(self, config: dict, dest_key: str):
        """Every worker must implement this specific method."""
        pass


# S3 Worker
class S3Worker(BaseIngestor):
    def __init__(self, s3_client, bucket):
        self.s3 = s3_client
        self.bucket = bucket

    def ingest(self, config: dict, dest_key: str):
        url = config.get("url")
        log.info("s3_worker_start", url=url)
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            self.s3.upload_fileobj(r.raw, self.bucket, dest_key)


# API worker (Weather Dimensions)
class APIWorker(BaseIngestor):
    def __init__(self, s3_client, bucket):
        self.s3 = s3_client
        self.bucket = bucket

    def ingest(self, config: dict, dest_key: str):
        # OpenWeatherAPI needs specific params (lat, lon, appid)
        api_key = config.get("api_key")
        endpoint = "https://api.openweathermap.org/data/2.5/weather"

        log.info("api_worker_start", source="openweather")
        response = requests.get(endpoint, params=config["params"])
        response.raise_for_status()

        # Uploading raw JSON string to Bronze
        self.s3.put_object(Bucket=self.bucket, Key=dest_key, Body=response.text)


# TODO: IAM role: BronzeIngestor needs permission to read from the Internet (requests) and write to the Bronze S3 Bucket.
class BronzeIngestor:
    def __init__(self, source_id: str):
        self.source_id = source_id
        self.config = self._load_config()
        # In LocalStack/Docker: http://localstack:4566
        # In AWS: None (Boto3 handles it automatically)
        endpoint = os.getenv("AWS_ENDPOINT_URL")

        self.s3 = boto3.client("s3", endpoint_url=endpoint)
        self.bucket = os.getenv("BRONZE_BUCKET")

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
