import json
import os
import time
from kafka import KafkaConsumer
from pymongo import MongoClient
from datetime import datetime

print("Starting Basic Consumer...")

# Wait for services to be ready
time.sleep(10)

# Configuration
KAFKA_BROKER = 'kafka:29092'
KAFKA_TOPIC = 'reddit-stream'
MONGO_URI = 'mongodb://new_user300:Sulaimon1@mongodb:27017/reddit_data?authSource=admin'

print(f"Connecting to MongoDB...")
client = MongoClient(MONGO_URI)
db = client['reddit_data']
collection = db['processed_posts']
print(f"MongoDB connected. Current documents: {collection.count_documents({})}")

print(f"Connecting to Kafka at {KAFKA_BROKER}...")
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',  # Read from beginning
    enable_auto_commit=True,
    group_id='reddit-consumer-group'
)

print(f"Connected! Consuming messages...")

count = 0
for message in consumer:
    try:
        data = message.value
        data['processed_at'] = datetime.utcnow()
        data['sentiment_label'] = 'neutral'
        
        collection.insert_one(data)
        count += 1
        print(f"Processed {count} messages. Latest: {data.get('type')} from r/{data.get('subreddit')}")
        
    except Exception as e:
        print(f"Error: {e}")
        continue