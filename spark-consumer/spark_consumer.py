"""
Spark Structured Streaming Consumer
Consumes messages from Kafka, processes them, and stores in MongoDB
"""
import os
import json
import logging
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pymongo import MongoClient
from transformations import clean_text, analyze_sentiment, detect_language, extract_entities

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'reddit-stream')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'reddit_data')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'processed_posts')

class SparkStreamProcessor:
    """
    Processes streaming data from Kafka using Spark Structured Streaming
    """
    
    def __init__(self):
        """Initialize Spark session and MongoDB connection"""
        self.spark = self._create_spark_session()
        self.mongo_client = None
        self._setup_mongodb()
    
    def _create_spark_session(self):
        """
        Create and configure Spark session
        
        Returns:
            SparkSession: Configured Spark session
        """
        return SparkSession.builder \
            .appName("RedditStreamProcessor") \
            .config("spark.streaming.stopGracefullyOnShutdown", "true") \
            .config("spark.sql.shuffle.partitions", "2") \
            .config("spark.sql.streaming.schemaInference", "true") \
            .getOrCreate()
    
    def _setup_mongodb(self):
        """Setup MongoDB connection"""
        try:
            self.mongo_client = MongoClient(MONGO_URI)
            self.db = self.mongo_client[MONGO_DATABASE]
            self.collection = self.db[MONGO_COLLECTION]
            
            # Create indexes for better query performance
            self.collection.create_index([("timestamp", -1)])
            self.collection.create_index([("type", 1)])
            self.collection.create_index([("subreddit", 1)])
            self.collection.create_index([("sentiment_label", 1)])
            
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

def process_batch(self, batch_df, batch_id):
    """Process a micro-batch of data"""
    try:
        if not batch_df.isEmpty():
            pandas_df = batch_df.toPandas()
            logger.info(f"Processing batch {batch_id} with {len(pandas_df)} records")
            
            processed_records = []
            for _, row in pandas_df.iterrows():
                try:
                    # Parse JSON value
                    data = json.loads(row['value'])
                    
                    # Determine text field based on type
                    if data['type'] == 'submission':
                        text = f"{data.get('title', '')} {data.get('text', '')}"
                    else:  # comment
                        text = data.get('body', '')
                    
                    # Apply transformations (simplified for debugging)
                    processed_record = {
                        **data,  # Original data
                        'cleaned_text': text[:500] if text else '',  # Limit text length
                        'sentiment_label': 'neutral',  # Simplified for now
                        'language': 'en',
                        'processed_at': datetime.utcnow(),
                        'batch_id': str(batch_id)  # Convert to string
                    }
                    
                    processed_records.append(processed_record)
                    
                except Exception as e:
                    logger.error(f"Error processing record: {e}")
                    continue
            
            # Bulk insert to MongoDB
            if processed_records:
                try:
                    result = self.collection.insert_many(processed_records, ordered=False)
                    logger.info(f"Inserted {len(result.inserted_ids)} records in batch {batch_id}")
                except Exception as e:
                    logger.error(f"MongoDB insert error: {e}")
                    # Try inserting one by one as fallback
                    for record in processed_records:
                        try:
                            self.collection.insert_one(record)
                        except Exception as e2:
                            logger.error(f"Failed to insert single record: {e2}")
                    
    except Exception as e:
        logger.error(f"Error processing batch {batch_id}: {e}")
    
    def start_streaming(self):
        """
        Start the streaming pipeline
        """
        # Define schema for Kafka messages
        kafka_schema = StructType([
            StructField("key", StringType()),
            StructField("value", StringType()),
            StructField("topic", StringType()),
            StructField("partition", IntegerType()),
            StructField("offset", LongType()),
            StructField("timestamp", TimestampType()),
            StructField("timestampType", IntegerType())
        ])
        
        # Read stream from Kafka
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BROKER) \
            .option("subscribe", KAFKA_TOPIC) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()
        
        # Select relevant columns
        df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
        
        # Process stream with foreachBatch
        query = df.writeStream \
            .foreachBatch(self.process_batch) \
            .outputMode("append") \
            .trigger(processingTime="10 seconds") \
            .option("checkpointLocation", "/tmp/checkpoint") \
            .start()
        
        logger.info("Streaming started. Waiting for data...")
        
        # Wait for termination
        query.awaitTermination()
    
    def stop(self):
        """Clean up resources"""
        if self.mongo_client:
            self.mongo_client.close()
        if self.spark:
            self.spark.stop()

if __name__ == "__main__":
    processor = SparkStreamProcessor()
    try:
        processor.start_streaming()
    except KeyboardInterrupt:
        logger.info("Stopping stream processor...")
        processor.stop()