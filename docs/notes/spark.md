# Best Practices for Using Spark and PySpark
* Use DataFrames over RDDs for performance and optimizations 
* Cache datasets only when reused multiple times 
* Avoid using collect() on large datasets 
* Use partitioning and repartition() to optimize performance 
* Enable dynamic resource allocation in Spark configs 
* Profile and monitor jobs using Spark UI 
# Data Ingestion & Schema Stability
* Disable Vectorized Reader for Bronze Ingestion:
  - Use .config("spark.sql.parquet.enableVectorizedReader", "false") when reading raw/untrusted Parquet files to avoid JVM crashes caused by type mismatches (e.g., INT32 vs INT64).
* Enable Vectorization for Trusted Layers:
  - Always keep vectorization true for Silver and Gold layers to utilize SIMD CPU optimizations and increase throughput by 3x–10x.
* Explicit Casting is Mandatory
  - Never rely on Spark's "Inference." Always use .cast() in your transformation logic to define a strict Data Contract.
* Prefer Iceberg/Delta for Metadata:
  - Use modern table formats to skip file listing overhead and enable "Partition Pruning" at the metadata level.
# troubleshooting 
## Resolving Parallel Schema Discovery Failures
Environment: PySpark 3.5, Iceberg, S3 (LocalStack), Parquet Source

1. The Problem: "The BigInt vs. Int Trap"
When processing large-scale Parquet datasets (like NYC Taxi data), different files in the same directory often have inconsistent metadata. In this case, some files used INT for VendorID while others used BIGINT.

2. The Error:
Caused by: org.apache.spark.SparkException: [CANNOT_MERGE_INCOMPATIBLE_DATA_TYPE] 
Failed to merge incompatible data types "BIGINT" and "INT".

Spark performs Schema Discovery the moment spark.read.parquet() is called with a wildcard path.
Because Spark tries to build a Logical Plan before executing any code, it crashes during the metadata scan—even if you have a .cast() or .select() later in your script.
The "Lazy Evaluation" doesn't save you because the "Planning Phase" fails first.

3. The Solution: "Suppression & Manual Enforcement"
The fix required a two-pronged approach: disabling Spark’s automatic "intelligence" and replacing it with manual schema enforcement.

A. Session-Level Configuration (spark_setup.py)
I modified the SparkSession to stop the Catalyst Optimizer from attempting a global schema merge.

* `spark.sql.parquet.mergeSchema = "false"`
  - Tells Spark to take the schema of the first file it finds and stop comparing it to others.

* `spark.sql.files.ignoreCorruptFiles = "true"`
  - Prevents job failure if footer metadata is inconsistent.

* `spark.sql.parquet.enableVectorizedReader = "false"`
  - Disables the high-speed reader which is strictly typed, falling back to a more flexible row-based reader that allows for manual casting.

B. Implementation Pattern (silver_transform.py)
I implemented a Naked Read followed by Immediate Normalization.
```python
# 1. READ: Bypass internal validation by avoiding .option("mergeSchema", "true")
df = spark.read.parquet("s3a://bronze/nyc_taxi/year=*/month=*/*.parquet")

# 2. TRANSFORM: Manually 'Force' the schema before any Action (like .distinct() or .write())
silver_df = df.select(
    F.col("VendorID").cast("long").alias("vendor_id"), # Resolves the INT/BIGINT conflict
    F.col("tpep_pickup_datetime").alias("pickup_time"),
    # ... other columns
)
```
## learning review
The Technical Insight: This issue requires and provides an understanding of the Spark Lifecycle.
Debugging this required knowing that schema validation is part of the Analysis Phase, which happens before the Physical Plan is generated.
Medallion Architecture: This is a core competency for the Bronze-to-Silver transition.
The Bronze layer is often "messy" and inconsistent; the Silver layer is where strict types and business logic are enforced.
Performance Trade-off: While disabling vectorizedReader can be slower, it is a necessary trade-off for robustness when dealing with legacy or inconsistent source data.
