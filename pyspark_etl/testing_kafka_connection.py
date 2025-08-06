from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple schema for testing
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

# Kafka configuration for localhost
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "crashes"

logger.info(f"Connecting to Kafka broker: {KAFKA_BROKER}")
logger.info(f"Subscribing to Kafka topic: {KAFKA_TOPIC}")

# Create Spark session
spark = SparkSession.builder \
    .appName("KafkaTestConsumer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1") \
    .config("spark.sql.adaptive.enabled", "false") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "false") \
    .getOrCreate()

# Set log level to reduce noise
spark.sparkContext.setLogLevel("WARN")

logger.info("Spark session created successfully")

print("="*50)
print("STEP 1: Testing Raw Kafka Connection")
print("="*50)

# Read from Kafka
df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

logger.info("Kafka stream created")

# Test 1: Raw Kafka messages
def test_raw_kafka(batch_df, batch_id):
    print(f"\n=== RAW KAFKA TEST - BATCH {batch_id} ===")
    count = batch_df.count()
    print(f"Messages received: {count}")
    
    if count > 0:
        print("Raw Kafka message structure:")
        batch_df.printSchema()
        
        print("Sample raw messages (showing key, value, topic, partition):")
        batch_df.select(
            col("key").cast("string").alias("key"),
            col("value").cast("string").alias("value"),
            col("topic"),
            col("partition"),
            col("offset")
        ).show(3, truncate=False)
    else:
        print("No messages received in this batch")

# Start raw Kafka test
raw_test_query = df_kafka.writeStream \
    .foreachBatch(test_raw_kafka) \
    .outputMode("append") \
    .trigger(processingTime='5 seconds') \
    .start()

print("Raw Kafka test started. Waiting for messages...")
print("Send some messages to the 'crashes' topic and watch the output...")

import time
time.sleep(30)  # Wait 30 seconds for messages

print("\n" + "="*50)
print("STEP 2: Testing JSON Parsing")
print("="*50)

# Test 2: JSON parsing
df_json_strings = df_kafka.selectExpr("CAST(value AS STRING) as json_string")

def test_json_parsing(batch_df, batch_id):
    print(f"\n=== JSON PARSING TEST - BATCH {batch_id} ===")
    count = batch_df.count()
    print(f"JSON strings to parse: {count}")
    
    if count > 0:
        print("Raw JSON strings:")
        batch_df.show(2, truncate=False)
        
        # Try parsing
        try:
            parsed_df = batch_df.select(from_json(col("json_string"), incident_schema).alias("parsed_data"))
            parsed_count = parsed_df.filter(col("parsed_data").isNotNull()).count()
            print(f"Successfully parsed records: {parsed_count}")
            
            if parsed_count > 0:
                print("Parsed data sample:")
                parsed_df.select("parsed_data.*").show(2, truncate=False)
                
                print("Schema of parsed data:")
                parsed_df.select("parsed_data.*").printSchema()
            else:
                print("WARNING: No records were successfully parsed!")
                print("This might indicate a schema mismatch.")
                
        except Exception as e:
            print(f"ERROR parsing JSON: {e}")

json_test_query = df_json_strings.writeStream \
    .foreachBatch(test_json_parsing) \
    .outputMode("append") \
    .trigger(processingTime='5 seconds') \
    .start()

time.sleep(30)  # Wait for JSON parsing test

print("\n" + "="*50)
print("STEP 3: Testing Vehicle Types Extraction")
print("="*50)

# Test 3: Vehicle types processing
df_parsed = df_json_strings.select(from_json(col("json_string"), incident_schema).alias("data")).select("data.*")

def test_vehicle_processing(batch_df, batch_id):
    print(f"\n=== VEHICLE PROCESSING TEST - BATCH {batch_id} ===")
    count = batch_df.count()
    print(f"Total parsed records: {count}")
    
    if count > 0:
        # Check vehicle_types column
        vehicle_data = batch_df.select("incident_id", "vehicle_types", "vehicle_type_id")
        print("Vehicle types data:")
        vehicle_data.show(3, truncate=False)
        
        # Check for non-null vehicle_types
        non_null_vehicles = batch_df.filter(col("vehicle_types").isNotNull())
        non_null_count = non_null_vehicles.count()
        print(f"Records with non-null vehicle_types: {non_null_count}")
        
        if non_null_count > 0:
            # Try exploding vehicle types
            from pyspark.sql.functions import posexplode, size
            
            # Filter records that have vehicle_types array with elements
            valid_vehicles = batch_df.filter(
                col("vehicle_types").isNotNull() & (size(col("vehicle_types")) > 0)
            )
            valid_count = valid_vehicles.count()
            print(f"Records with valid vehicle_types arrays: {valid_count}")
            
            if valid_count > 0:
                # Explode vehicle types
                exploded = valid_vehicles.select(
                    col("vehicle_type_id").alias("vehicle_id"),
                    posexplode("vehicle_types").alias("vehicle_position", "vehicle_type")
                ).select(
                    "vehicle_id",
                    "vehicle_type", 
                    (col("vehicle_position") + 1).alias("vehicle_position")
                )
                
                exploded_count = exploded.count()
                print(f"Exploded vehicle records: {exploded_count}")
                
                if exploded_count > 0:
                    print("Sample exploded vehicle data:")
                    exploded.show(5, truncate=False)
                else:
                    print("No exploded records generated!")
            else:
                print("No records with valid vehicle_types arrays found!")
        else:
            print("No records with non-null vehicle_types found!")

vehicle_test_query = df_parsed.writeStream \
    .foreachBatch(test_vehicle_processing) \
    .outputMode("append") \
    .trigger(processingTime='5 seconds') \
    .start()

time.sleep(30)  # Wait for vehicle processing test

print("\n" + "="*50)
print("STEP 4: Simple Console Output Test")
print("="*50)

# Test 4: Simple console output
simple_console_query = df_parsed.select("incident_id", "borough", "vehicle_types").writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .trigger(processingTime='10 seconds') \
    .start()

print("Console output test started. You should see data below:")
time.sleep(60)  # Let it run for 1 minute

print("\n" + "="*50)
print("TESTS COMPLETED")
print("="*50)

# Stop all queries
print("Stopping all test queries...")
for query in spark.streams.active:
    query.stop()

print("All tests completed. Check the output above for any issues.")
print("\nSummary of what to look for:")
print("1. Raw Kafka messages should show JSON data")
print("2. JSON parsing should show structured data")
print("3. Vehicle processing should show exploded vehicle types")
print("4. Console output should show final processed records")

spark.stop()