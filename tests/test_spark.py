from pyspark.sql import SparkSession

# Simple test to check if the JVM and Spark talk to each other
spark = SparkSession.builder.appName("SmokeTest").getOrCreate()
df = spark.createDataFrame([{"hello": "world"}, {"hello": "spark"}])
df.show()
spark.stop()
