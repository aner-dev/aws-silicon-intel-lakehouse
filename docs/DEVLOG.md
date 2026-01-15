## 🛠 Debug Log: S3A Configuration (NumberFormatException)
file: src/transform/bronze_to_silver.py

### Precedence Note
Even though the environment continued to "leak" the '60s' string, my **Explicit Configuration** took precedence. By setting these values directly in the `SparkSession` builder with the `spark.hadoop.` prefix, I successfully **shadowed** the faulty system-wide settings.

### Issue
Spark failed to initialize the S3A filesystem when connecting to LocalStack.
**Error:** `java.lang.NumberFormatException: For input string: "60s"` (or "24h").

### Root Cause
The environment (Artix Linux OS or Hadoop defaults) was providing duration strings with units (e.g., '60s'), but the S3A connector expected **pure numeric Longs**. The Java parser crashed when encountering the 's' or 'h' characters.
**Type Mismatch** caused by **Legacy Parsing**:
* The Java driver (the low-level layer that handles S3 communication) was using a legacy parser.
* It lacked the "adaptability" to translate ISO-8601 strings (like `60s`) into integers (`60000`).
* When the parser encountered the character 's', it triggered a `NumberFormatException` and halted the Spark session initialization.
### Solution
Applied **Explicit Configuration Overrides** in the `SparkSession` builder.
1. Use the `spark.hadoop.` prefix to target the S3A driver directly.
2. Provide pure numeric strings (e.g., `"60000"` for milliseconds).
3. Disable the S3A implementation cache to prevent "Ghost Configs" from reappearing.

### Key Settings
- `fs.s3a.connection.timeout`: 60000
- `fs.s3a.multipart.purge.age`: 86400
- `fs.s3a.impl.disable.cache`: true
### abstract 
Modern Spark/Hadoop (Newer): It is becoming very common to use "Human Readable" strings like 24h, 10m, or 500ms. This is called **ISO-8601 Duration format**
Legacy Spark/Hadoop (Older): The older systems strictly require Integers (Longs). They usually assume a specific unit (e.g., "this field is always in milliseconds").

# Data Quality Checks through Great Expectations
Data Validation as a first-class citizen: 
I treat data validation as a first-class citizen by embedding Great Expectations directly into my CI/CD pipeline. 
If the data doesn't meet the quality standards, the pipeline is blocked from progressing to the Gold layer.
Use of **automated assertions** to ensure schema consistency across all environments.
# Partitioning & Pruning: Performance approaches 
- Data partitioning is the *logical approach* 
- Hive partitioning is the *physical implementation* of that approach
  - Define the name of a column as a key-value pair 'amazon=categories/'
- And the combination of both allows pyspark to do 'Partition Pruning'
# resource optimization and early validation (spark = SparkSessionFactory.get_session())
spark = SparkSessionFactory.get_session() is the *most expensive line of code* in a transformation script
* When that line runs:
  * A JVM (Java Virtual Machine) starts.
  * Memory is allocated (RAM is reserved).
  * The Spark Driver initializes.
  * In a real cluster, Executors are requested from the resource manager.
## 'golden order of execution' 
* Input Validation: Check if the date string is correct.
* Path Construction: Build your bronze_path string.
* Metadata Check: Use boto3 (which is very cheap/fast) to check if the files actually exist in S3.
* The Point of No Return: ONLY NOW do you start the SparkSession.

# Resolving Test Suite Path Mapping (Pytest)

## Problem
When running `pytest` from the project root, the test runner failed to locate the source code inside the `src/` directory. This resulted in `ModuleNotFoundError: No module named 'src'` (or missing sub-modules like `utils`), because the `src/` folder was not in Python’s search path by default.

## Solution: Pytest Path Mapping
Instead of using manual `sys.path` inserts or setting temporary shell environment variables, I configured the `pyproject.toml` file to natively map the source directory.

### Configuration Addition
```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```
# iceberg catalog & aws glue 
Designed a Lakehouse architecture using Apache Iceberg with a pluggable catalog layer.
Local development used Iceberg’s native catalog; production deployments target AWS Glue Data Catalog.
















