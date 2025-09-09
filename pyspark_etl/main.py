from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col,to_timestamp, to_date, date_format,year, month, hour, regexp_replace, when, regexp_extract, concat, lit, lpad, length, ascii, substring
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType
from pyspark.sql.functions import explode, sha2, concat_ws,dayofweek,posexplode, lit, expr, sum, size, count
import os
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

incident_schema = StructType([
    StructField("incident_id", StringType()),
    StructField("timestamp", StringType()),
    StructField("crash_date", StringType()),
    StructField("crash_time", StringType()),
    StructField("location_id", StringType()),
    StructField("borough", StringType()),
    StructField("zip_code", StringType()),
    StructField("on_street_name", StringType()),
    StructField("off_street_name", StringType()),
    StructField("cross_street_name", StringType()),
    StructField("vehicle_type_id", StringType()),
    StructField("vehicle_types", ArrayType(StringType())),
    StructField("cont_factors_id", StringType()),
    StructField("contributing_factors", ArrayType(StringType())),
    StructField("number_of_persons_injured", IntegerType()),
    StructField("number_of_persons_killed", IntegerType()),
    StructField("number_of_motorist_injured", IntegerType()),
    StructField("number_of_motorist_killed", IntegerType()),
    StructField("number_of_cyclist_injured", IntegerType()),
    StructField("number_of_cyclist_killed", IntegerType()),
    StructField("number_of_pedestrians_injured", IntegerType()),
    StructField("number_of_pedestrians_killed", IntegerType())
])

DEBUG = True
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "crashes"
PG_URL =  "jdbc:postgresql://postgres:5432/NycTrafficStreamDatabase"
PG_USER = "admin"
PG_PASSWORD = "admin123"

logger.info(f"Connecting to Kafka broker: {KAFKA_BROKER}")
logger.info(f"Subscribing to Kafka topic: {KAFKA_TOPIC}")
logger.info(f"PostgreSQL URL: {PG_URL}")

spark = SparkSession.builder \
    .appName("KafkaToPostgresETL") \
    .config("spark.jars.packages", ",".join([
        "org.postgresql:postgresql:42.7.2",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"
    ])) \
    .getOrCreate()
    
spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")



logger.info("Spark session created successfully")

df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

logger.info("Kafka stream created")

df_json = df_kafka.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), incident_schema).alias("data")) \
    .select("data.*")

df_json.printSchema()

print(f"Password: '{PG_PASSWORD}'")
print(f"User: '{PG_USER}'")
print(f"URL: '{PG_URL}'")




logger.info("JSON parsing configured")



def write_to_postgres(table_name):
    def _write(batch_df, batch_id):
        try:
            print(f"Writing batch {batch_id} to {table_name}")
            batch_df.show(truncate=False)
            batch_df.write \
                .format("jdbc") \
                .option("url", os.getenv("PG_URL")) \
                .option("dbtable", table_name) \
                .option("user", os.getenv("PG_USER")) \
                .option("password", os.getenv("PG_PASSWORD")) \
                .option("driver", "org.postgresql.Driver") \
                .option("sslmode", "disable") \
                .option("stringtype", "unspecified")\
                .mode("append") \
                .save()
        except Exception as e:
            print(f"Error writing batch {batch_id} to {table_name}: {e}")
    return _write



def process_batch(batch_df, batch_id):
    print(f"\n=== Batch {batch_id} ===")
    batch_df.show(truncate=False)

    print(f"\n=== Batch {batch_id} - Inspecting timestamp_clean ===")
    

    df_vehicle = batch_df \
        .where(col("vehicle_types").isNotNull()) \
        .select(
            col("vehicle_type_id").alias("vehicle_id"),
            posexplode("vehicle_types").alias("vehicle_position", "vehicle_type")
        ) \
        .select("vehicle_id", "vehicle_type", (col("vehicle_position") + 1).alias("vehicle_position")) \
        .dropDuplicates(["vehicle_id"])

    df_vehicle.write \
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
    
    df_clean = batch_df.withColumn(
    "timestamp_clean",
    regexp_replace(
        regexp_replace(
            "timestamp",
            r"(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}\.\d{3}T(\d{1,2}):(\d{2}:\d{2})Z",
            "$1 $2:$3"
        ),
        r"(\d{4}-\d{2}-\d{2}) (\d):(\d{2}:\d{2})",
        "$1 0$2:$3"
    )
    )
    
    print(f"\n=== Batch {batch_id} - Fixed timestamp_clean ===")
    df_clean.select("timestamp", "timestamp_clean").show(truncate=False, n=50)

    df_clean.select("timestamp_clean", length("timestamp_clean"), substring("timestamp_clean", 10, 1).alias("char_at_10")).show()


    dim_date = df_clean \
        .withColumn("date_id", to_timestamp("timestamp_clean", "yyyy-MM-dd H:mm:ss")) \
        .withColumn("crash_date_parsed", to_date("timestamp_clean", "yyyy-MM-dd")) \
        .withColumn("day_of_week", date_format("date_id", "EEEE")) \
        .withColumn("month_name", date_format("date_id", "MMMM")) \
        .withColumn("hour_of_day", hour("date_id")) \
        .withColumn("year", year("date_id")) \
        .select(
            col("date_id"),
            col("crash_date_parsed").alias("crash_date"),
            col("day_of_week"),
            col("month_name").alias("month"),
            col("hour_of_day"),
            col("year")
        ).dropDuplicates(["date_id"])
    
    print("Batch ID:", batch_id)
    print("Count before writing dim_date:", dim_date.count())
    dim_date.show(truncate=False)
    print("dim_date count:", dim_date.count())

    dim_date.write \
        .format("jdbc") \
        .option("url", PG_URL) \
        .option("dbtable", "public.dim_date") \
        .option("user", PG_USER) \
        .option("password", PG_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .option("sslmode", "disable") \
        .option("stringtype", "unspecified") \
        .mode("append") \
        .save()

    dim_factors = batch_df \
        .select(col("cont_factors_id"), posexplode("contributing_factors").alias("factor_position", "factor_description")) \
        .select("cont_factors_id", "factor_description", "factor_position") \
        .dropDuplicates(["cont_factors_id", "factor_position"])

    dim_factors.write \
        .format("jdbc") \
        .option("url", PG_URL) \
        .option("dbtable", "public.dim_contributing_factor") \
        .option("user", PG_USER) \
        .option("password", PG_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .option("sslmode", "disable") \
        .option("stringtype", "unspecified") \
        .mode("append") \
        .save()

    dim_location = batch_df \
        .select("location_id", "borough", "zip_code", "on_street_name", "off_street_name", "cross_street_name") \
        .dropDuplicates(["location_id"])

    dim_location.write \
        .format("jdbc") \
        .option("url", PG_URL) \
        .option("dbtable", "public.dim_location") \
        .option("user", PG_USER) \
        .option("password", PG_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .option("sslmode", "disable") \
        .option("stringtype", "unspecified") \
        .mode("append") \
        .save()

    print(f"Batch {batch_id} processed successfully.")


query = df_json.writeStream \
    .foreachBatch(process_batch) \
    .option("checkpointLocation", "/tmp/checkpoints/all_dimensions") \
    .start()

query.awaitTermination()
