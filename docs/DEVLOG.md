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

