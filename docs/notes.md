# Partitioning 
- code example: silver_df.write.mode("overwrite").parquet(silver_path) -> /001 󰌠  bronze_to_silver.py
- Partitioning by **Date** is best practice 
# iceberg in silver layer (Reasons to avoid vanilla/plain parquet)
- before: script_silver_layer.py without use apache iceberg, simply loading the parquet proceessed with pyspark to AWS s3
- now: use iceberg to enrich the parquet with metadata (JSON, avro ft)
  - providing such capacities as *schema evolution, time travel & ACID transactions* 
## Storage Layer: File Formats vs Table Formats

### 1. Parquet (The File Format)
- **Role:** How data is physically stored on disk (Columnar).
- **Pros:** High compression, fast reads for specific columns.
- **Cons:** No transaction support, slow schema discovery at scale, risky concurrent reads/writes.

### 2. Apache Iceberg (The Table Format)
- **Role:** A management layer sitting ON TOP of Parquet files.
- **Why Silver Layer uses Iceberg:**
    - **ACID Compliance:** Prevents data corruption during failed jobs.
    - **Time Travel:** Enables rollbacks and auditing of historical data versions.
    - **Schema Evolution:** Update table structures (add/rename columns) without rewriting data.
    - **Hidden Partitioning:** Spark doesn't need to scan every folder; Iceberg knows exactly where the data is via metadata.

### Conclusion
Converting to Parquet is **not** a bad practice, but leaving it as "Pure Parquet" in the Silver/Gold layers is considered **Legacy Architecture**. Modern Lakehouses use Iceberg/Delta/Hudi to turn those files into professional, reliable tables.

# schema enforcement 
* directly define the schema in the silver_processing file (pyspark)
* take the control and dictate to the engine the exactly structures that it should expect 
* instead of leave the motor *infer* that structure (Schema Inference) 
  - An unnecessary *READ-in-memory* and a bad/suboptimal approach for Big Data production
