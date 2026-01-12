# Architecture Decision Record (ADR)

## 📝 ADR 0002: Transition to NYC Transit Dataset

**Status:** Proposed  
**Date:** 2024-05-22  

---

### 1. Context
The initial prototype used the **NewsAPI**. While sufficient for a basic "Bronze-to-Silver" pipeline, it presented several limitations for a production-grade AWS Lakehouse demonstration, specifically regarding data volume and schema variety.

### 2. Decision
I'm replacing NewsAPI with the **NYC Taxi (Yellow)** and **High Volume For-Hire Vehicle (HVFHV)** datasets, supplemented by the **Taxi Zone Lookup** reference data.

---

### 3. Rationale (Why this change?)

| Reason | Description |
| :--- | :--- |
| **Right-sizing the Tech Stack** | NewsAPI datasets were under 50MB. PySpark is designed for distributed computing; using it on tiny JSON files was "overkill." The NYC datasets provide millions of rows, justifying the use of Spark's distributed processing. |
| **Schema Complexity** | NewsAPI had a flat, simple structure. The NYC data includes complex timestamps, geospatial IDs, and itemized financial breakdowns, allowing for more advanced Silver-layer cleaning. |
| **Relational Integrity** | To demonstrate true **Dimensional Modeling (Star Schema)**, we need a Fact table (Trips) and a Dimension table (Zones). NewsAPI did not provide a natural "Lookup" table. |
| **Multi-Format Ingestion** | This change allows us to demonstrate handling **Parquet** (Trips) and **CSV** (Zones) in the same pipeline. |
| **Business Logic Context** | The 2025/2026 data includes congestion fees, providing a great opportunity for complex "Gold layer" transformations. |

---

### 4. Implementation Notes
* **Bronze Layer:** Raw Parquet files stored in `s3://bucket/bronze/nyc_taxi/`.
* **Silver Layer:** Cleaned and deduplicated Iceberg tables partitioned by `pickup_time`.
* **Catalog:** Managed via AWS Glue for integration with Amazon Athena.
