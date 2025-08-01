import os
from pyspark.sql import SparkSession
import uuid


# Read env vars (with your defaults)
PG_URL = "jdbc:postgresql://postgres:5432/NycTrafficStreamDatabase"
PG_USER = "admin"
PG_PASSWORD = "admin123"

spark = SparkSession.builder \
    .appName("MockInsertToDimVehicle") \
    .getOrCreate()
spark.sparkContext.setLogLevel("DEBUG")

# Create a small DataFrame with mock data
df_mock = spark.createDataFrame([
    (str(uuid.uuid4()), "Sedan", 1)
], ["vehicle_id", "vehicle_type", "vehicle_position"])

print(f"Password: '{PG_PASSWORD}'")
print(f"User: '{PG_USER}'")
print(f"URL: '{PG_URL}'")

try:
    print("Attempting to write to public.dim_vehicle...")
    df_mock.write \
        .format("jdbc") \
        .option("url", PG_URL) \
        .option("dbtable", "public.dim_vehicle") \
        .option("user", PG_USER) \
        .option("password", PG_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .option("sslmode", "disable") \
        .option("stringtype", "unspecified") \
        .mode("append") \
        .save()
    print("Mock insert to dim_vehicle done!")
except Exception as e:
    print("Spark write failed with exception:")
    print(e)


print("Mock insert to dim_vehicle done!")
