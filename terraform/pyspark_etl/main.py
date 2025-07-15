from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType
import os

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

spark = SparkSession.builder \
    .appName("KafkaToPostgresETL") \
    .config("spark.jars.packages", ",".join([
        "org.postgresql:postgresql:42.7.3", 
        "org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.1"  
    ])) \
    .getOrCreate()


df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "crashes") \
    .option("startingOffsets", "latest") \
    .load()

df_json = df_kafka.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), incident_schema).alias("data")) \
    .select("data.*")

df_json.printSchema()



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


# inserting data into dim_vehicle
df_vehicle = df_json.select(
    posexplode("vehicle_types").alias("pos", "vehicle_type"),
    posexplode("vehicle_type_ids").alias("pos2", "vehicle_id")
).where(col("pos") == col("pos2")).select("vehicle_id", "vehicle_type", (col("pos") + 1).alias("vehicle_position"))





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

# for location dimension
df_location = df_json.select(
    col("location_id"),
    col("borough"),
    col("zip_code"),
    col("on_street_name"),
    col("cross_street_name"),
    col("off_street_name")
).dropna(subset=["borough", "on_street_name"])

df_location = df_location.dropDuplicates()


#for contributing factor dimension

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

# Define fact_incidents DataFrame
df_fact_incidents = df_json.select(
    col("incident_id"),
    to_timestamp(col("timestamp"), "yyyy-MM-dd'T'HH:mm:ssX").alias("date_id"),
    col("location_id"),
    # Assuming vehicle_type_id is the FK for dim_vehicle for the primary vehicle.
    # dim_vehicle handles multiple vehicle types per incident separately.
    col("vehicle_type_id").alias("vehicle_id"),
    # Assuming cont_factors_id is the FK for dim_contributing_factor for the primary/aggregate factor.
    # dim_contributing_factor handles individual factor descriptions separately.
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

# Write df_fact_incidents to PostgreSQL
df_fact_incidents.writeStream \
    .foreachBatch(write_to_postgres("fact_incidents")) \
    .outputMode("append") \
    .start()

# Aggregation for mv_incidents_by_borough_month
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

# foreachBatch writer for mv_incidents_by_borough_month (overwrite mode)
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

# Write stream for mv_incidents_by_borough_month
agg_borough_month_df.writeStream \
    .foreachBatch(write_mv_incidents_by_borough_month) \
    .outputMode("complete") \
    .start()

# Aggregation for mv_top_streets_by_injuries
agg_top_streets_df = df_json \
    .select(col("on_street_name"), col("number_of_persons_injured")) \
    .where(col("on_street_name").isNotNull() & (col("on_street_name") != "")) \
    .groupBy("on_street_name") \
    .agg(sum("number_of_persons_injured").alias("total_injured")) \
    .orderBy(col("total_injured").desc()) \
    .limit(10)

# foreachBatch writer for mv_top_streets_by_injuries (overwrite mode)
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

# Write stream for mv_top_streets_by_injuries
agg_top_streets_df.writeStream \
    .foreachBatch(write_mv_top_streets_by_injuries) \
    .outputMode("complete") \
    .start()

# Aggregation for mv_vehicle_type_incidents
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

# foreachBatch writer for mv_vehicle_type_incidents (overwrite mode)
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

# Write stream for mv_vehicle_type_incidents
agg_vehicle_type_df.writeStream \
    .foreachBatch(write_mv_vehicle_type_incidents) \
    .outputMode("complete") \
    .start()

# Aggregation for mv_incidents_by_borough_hour
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

# foreachBatch writer for mv_incidents_by_borough_hour (overwrite mode)
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

# Write stream for mv_incidents_by_borough_hour
agg_borough_hour_df.writeStream \
    .foreachBatch(write_mv_incidents_by_borough_hour) \
    .outputMode("complete") \
    .start()
