from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col,to_timestamp, to_date, date_format,year, month, hour
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
PG_PASSWORD =  "admin123"

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



df_vehicle = df_json \
    .where(col("vehicle_types").isNotNull()) \
    .select(
        col("vehicle_type_id").alias("vehicle_id"),
        posexplode("vehicle_types").alias("vehicle_position", "vehicle_type")
    ) \
    .select(
        "vehicle_id",
        "vehicle_type",
        (col("vehicle_position") + 1).alias("vehicle_position")
    ).dropDuplicates(["vehicle_id"])

query = df_json.writeStream \
    .format("console") \
    .option("truncate", False) \
    .outputMode("append") \
    .start()

df_vehicle.writeStream \
    .format("console") \
    .option("truncate", False) \
    .outputMode("append") \
    .start()


logger.info("beggining writing vehicle")

vehicle_write_query = df_vehicle.writeStream \
    .foreachBatch(write_to_postgres("public.dim_vehicle")) \
    .option("checkpointLocation", "/tmp/checkpoints/vehicle") \
    .start()

try:
    query.awaitTermination()
    vehicle_write_query.awaitTermination()
except KeyboardInterrupt:
    query.stop()
    vehicle_write_query.stop()

logger.info("finishing writing vehhicle and starting with date")


dim_date = df_json\
                    .withColumn("date_id",to_timestamp("timestamp"))\
                    .withColumn("crash_date_parsed", to_date("crash_date", "yyyy-MM-dd")) \
                    .withColumn("day_of_week", date_format("date_id", "EEEE")) \
                    .withColumn("month_name", date_format("date_id", "MMMM")) \
                    .withColumn("hour_of_day",hour("date_id"))\
                    .withColumn("year",year("date_id"))\
                    .select(
                        col("date_id").alias("date_id"),
                        col("crash_date_parsed").alias("crash_date"),
                        col("day_of_week").alias("day_of_week"),
                        col("month_name").alias("month"),
                        col("hour_of_day"),
                        col("year")
                    ).dropDuplicates(["date_id"])
                    
dim_date_write_query = dim_date.writeStream\
                       .foreachBatch(write_to_postgres("public.dim_date"))\
                       .option("checkpointLocation", "/tmp/checkpoints/dim_date") \
                       .start()
    
try:
    dim_date_write_query.awaitTermination()
except KeyboardInterrupt:
    dim_date_write_query.stop()

dim_date.writeStream\
    .format("console")\
    .option("truncate",False)\
    .outputMode("append")\
    .start().awaitTermination()
    
    
dim_factors = df_json\
                    .select(col('cont_factors_id'),
                            posexplode('contributing_factors').alias('factor_position','factor_description'))\
                    .select(
                        col('cont_factors_id'),
                        col('factor_description'),
                        col('factor_position')
                    ).dropDuplicates(['cont_factors_id','factor_position'])

dim_factors_write_query = dim_factors.writeStream\
                          .foreachBatch(write_to_postgres("public.dim_contributing_factor"))\
                          .option('checkpointLocation',"/tmp/checkpoints/dim_contributing_factor")\
                          .start()
                    
try:
    dim_factors_write_query.awaitTermination()
except KeyboardInterrupt:
    dim_factors_write_query.stop()
    
if DEBUG:
    dim_location = df_json\
               .select(col("location_id"),
                    col("borough"),
                    col("zip_code"),
                    col("on_street_name"),
                    col("off_street_name"),
                    col("cross_street_name")).dropDuplicates(["location_id"])
                     
dim_location.writeStream.format("console").option("truncate",False).outputMode("append").start().awaitTermination()

dim_location_write_query = dim_location.writeStream\
                            .foreachBatch(write_to_postgres("public.dim_location"))\
                            .option('checkpointLocation',"/tmp/checkpoints/dim_location")\
                            .start()
try:
    dim_location_write_query.awaitTermination()
except KeyboardInterrupt:
    dim_location_write_query.stop()