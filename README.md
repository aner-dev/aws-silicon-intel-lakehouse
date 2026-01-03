# aws-silicon-intel-lakehouse

[![Stack](https://img.shields.io/badge/Stack-AWS_Lakehouse-orange)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue)](LICENSE)

An automated Data Engineering ecosystem to track the **AI-Semiconductor market**. This project implements a modern Lakehouse architecture to process high-volume news data into actionable business intelligence.

---

## 🏗️ Architecture (Medallion)

```mermaid
graph LR
    subgraph "External"
        API[NewsAPI.org]
    end

    subgraph "Ingestion Layer"
        DLT[dlt / Airflow] -->|Raw JSON| Bronze[(S3 Bronze)]
    end

    subgraph "Processing Layer (Spark)"
        Bronze -->|Clean & Deduplicate| Silver[(S3 Silver)]
        Silver -->|Schema Evolution| Gold[(S3 Gold: Iceberg)]
    end

    subgraph "Infrastructure"
        LocalStack[LocalStack: S3 / Glue / Athena]
        Terraform[Terraform IaC]
    end

    API --> DLT
