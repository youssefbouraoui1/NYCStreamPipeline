from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType
import os
import logging

# Set up logging
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

# Get environment variables with defaults
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "crashes")
PG_URL = os.getenv("PG_URL", "jdbc:postgresql://postgres:5432/NycTrafficStreamDatabase")
PG_USER = os.getenv("PG_USER", "admin")
PG_PASSWORD = os.getenv("PG_PASSWORD", "admin123")

logger.info(f"Connecting to Kafka broker: {KAFKA_BROKER}")
logger.info(f"Subscribing to Kafka topic: {KAFKA_TOPIC}")
logger.info(f"PostgreSQL URL: {PG_URL}")

spark = SparkSession.builder \
    .appName("KafkaToPostgresETL") \
    .config("spark.jars.packages", ",".join([
        "org.postgresql:postgresql:42.7.3",
        "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1"
    ])) \
    .getOrCreate()




logger.info("Spark session created successfully")

df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

logger.info("Kafka stream created")

df_json = df_kafka.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), incident_schema).alias("data")) \
    .select("data.*")

df_json.printSchema()

logger.info("JSON parsing configured")


from pyspark.sql.functions import explode, sha2, concat_ws,to_date,date_format, year, month, dayofweek,to_timestamp,posexplode, hour, lit, expr, sum, size, count

def write_to_postgres(table_name):
    def _write(batch_df, batch_id):
        batch_df.write \
            .format("jdbc") \
            .option("url", os.getenv("PG_URL")) \
            .option("dbtable", table_name) \
            .option("user", os.getenv("PG_USER")) \
            .option("password", os.getenv("PG_PASSWORD")) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
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
    )
query = df_vehicle.writeStream \
    .format("console") \
    .outputMode("append") \
    .option("truncate", False) \
    .start()

query.awaitTermination()




df_vehicle.writeStream \
    .foreachBatch(write_to_postgres("dim_vehicle")) \
    .outputMode("update") \
    .start()

# now let us go to date dimension date

df_date = df_json.select(  to_timestamp("timestamp", "yyyy-MM-dd'T'HH:mm:ssX").alias("date_id"),
    to_date("crash_date", "yyyy-MM-dd").alias("crash_date"),
                         dayofweek(to_date("crash_date", "yyyy-MM-dd")).alias("day_of_week"),
    month(to_date("crash_date", "yyyy-MM-dd")).alias("month"),
    hour(to_timestamp("timestamp", "yyyy-MM-dd'T'HH:mm:ssX")).alias("hour_of_day"),
    year(to_date("crash_date", "yyyy-MM-dd")).alias("year")
).dropDuplicates(["date_id"])

df_date.writeStream \
    .foreachBatch(write_to_postgres("dim_date")) \
    .outputMode("update") \
    .start()

df_location = df_json.select(
    col("location_id"),
    col("borough"),
    col("zip_code"),
    col("on_street_name"),
    col("cross_street_name"),
    col("off_street_name")
).dropna(subset=["borough", "on_street_name"])

df_location = df_location.dropDuplicates()



df_factors = df_json.select(
    posexplode("contributing_factors").alias("factor_position_zero_based", "factor_description")
).withColumn(
    "factor_position", col("factor_position_zero_based") + 1
).withColumn(
    "factor_id", expr("uuid()")
).select("factor_id", "factor_description", "factor_position")

df_factors = df_factors.dropna().dropDuplicates(["factor_description", "factor_position"])

df_factors.writeStream \
    .foreachBatch(write_to_postgres("dim_contributing_factor")) \
    .outputMode("update") \
    .start()

df_fact_incidents = df_json.select(
    col("incident_id"),
    to_timestamp(col("timestamp"), "yyyy-MM-dd'T'HH:mm:ssX").alias("date_id"),
    col("location_id"),
    col("vehicle_type_id").alias("vehicle_id"),
    col("cont_factors_id").alias("contributing_factor_id"),
    col("number_of_persons_injured"),
    col("number_of_persons_killed"),
    col("number_of_motorist_injured"),
    col("number_of_motorist_killed"),
    col("number_of_pedestrians_injured"),
    col("number_of_pedestrians_killed"),
    col("number_of_cyclist_injured"),
    col("number_of_cyclist_killed")
).withColumn("number_of_incidents", lit(1))

df_fact_incidents.writeStream \
    .foreachBatch(write_to_postgres("fact_incidents")) \
    .outputMode("append") \
    .start()

agg_borough_month_df = df_json.select(
    col("borough"),
    year(to_date(col("crash_date"), "yyyy-MM-dd")).alias("year"),
    month(to_date(col("crash_date"), "yyyy-MM-dd")).alias("month"),
    col("number_of_persons_injured"),
    col("number_of_persons_killed")
).groupBy("borough", "year", "month") \
 .agg(
    sum("number_of_persons_injured").alias("total_injured"),
    sum("number_of_persons_killed").alias("total_killed")
)

def write_mv_incidents_by_borough_month(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", os.getenv("PG_URL")) \
        .option("dbtable", "mv_incidents_by_borough_month") \
        .option("user", os.getenv("PG_USER")) \
        .option("password", os.getenv("PG_PASSWORD")) \
        .option("driver", "org.postgresql.Driver") \
        .mode("overwrite") \
        .save()

agg_borough_month_df.writeStream \
    .foreachBatch(write_mv_incidents_by_borough_month) \
    .outputMode("complete") \
    .start()

agg_top_streets_df = df_json \
    .select(col("on_street_name"), col("number_of_persons_injured")) \
    .where(col("on_street_name").isNotNull() & (col("on_street_name") != "")) \
    .groupBy("on_street_name") \
    .agg(sum("number_of_persons_injured").alias("total_injured")) \
    .orderBy(col("total_injured").desc()) \
    .limit(10)

def write_mv_top_streets_by_injuries(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", os.getenv("PG_URL")) \
        .option("dbtable", "mv_top_streets_by_injuries") \
        .option("user", os.getenv("PG_USER")) \
        .option("password", os.getenv("PG_PASSWORD")) \
        .option("driver", "org.postgresql.Driver") \
        .mode("overwrite") \
        .save()

agg_top_streets_df.writeStream \
    .foreachBatch(write_mv_top_streets_by_injuries) \
    .outputMode("complete") \
    .start()

df_vehicle_exploded = df_json \
    .where(col("vehicle_types").isNotNull() & (size(col("vehicle_types")) > 0)) \
    .select(col("number_of_persons_killed"), posexplode(col("vehicle_types")).alias("vehicle_position_zero_based", "vehicle_type"))

agg_vehicle_type_df = df_vehicle_exploded \
    .withColumn("vehicle_position", col("vehicle_position_zero_based") + 1) \
    .groupBy("vehicle_type", "vehicle_position") \
    .agg(
        count(lit(1)).alias("total_incidents"),
        sum("number_of_persons_killed").alias("total_killed")
    )

def write_mv_vehicle_type_incidents(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", os.getenv("PG_URL")) \
        .option("dbtable", "mv_vehicle_type_incidents") \
        .option("user", os.getenv("PG_USER")) \
        .option("password", os.getenv("PG_PASSWORD")) \
        .option("driver", "org.postgresql.Driver") \
        .mode("overwrite") \
        .save()

agg_vehicle_type_df.writeStream \
    .foreachBatch(write_mv_vehicle_type_incidents) \
    .outputMode("complete") \
    .start()

agg_borough_hour_df = df_json.select(
    col("borough"),
    col("incident_id"),
    year(to_date(col("crash_date"), "yyyy-MM-dd")).alias("year"),
    month(to_date(col("crash_date"), "yyyy-MM-dd")).alias("month"),
    dayofweek(to_date(col("crash_date"), "yyyy-MM-dd")).alias("day_of_week"),
    hour(to_timestamp(col("timestamp"), "yyyy-MM-dd'T'HH:mm:ssX")).alias("hour_of_day"),
    col("number_of_persons_injured"),
    col("number_of_persons_killed")
).groupBy("borough", "hour_of_day", "year", "month", "day_of_week") \
 .agg(
    count("incident_id").alias("total_incidents"),
    sum("number_of_persons_injured").alias("total_injured"),
    sum("number_of_persons_killed").alias("total_killed")
)

def write_mv_incidents_by_borough_hour(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", os.getenv("PG_URL")) \
        .option("dbtable", "mv_incidents_by_borough_hour") \
        .option("user", os.getenv("PG_USER")) \
        .option("password", os.getenv("PG_PASSWORD")) \
        .option("driver", "org.postgresql.Driver") \
        .mode("overwrite") \
        .save()

agg_borough_hour_df.writeStream \
    .foreachBatch(write_mv_incidents_by_borough_hour) \
    .outputMode("complete") \
    .start()

logger.info("Starting all Spark streams...")

query = df_json.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

logger.info("Main query started. Waiting for termination...")

query.awaitTermination()
