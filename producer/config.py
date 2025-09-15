"""
Configuration management for Reddit Producer
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Reddit API Configuration
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
    REDDIT_SUBREDDITS = os.getenv('REDDIT_SUBREDDITS', 'all').split(',')
    
    # Kafka Configuration
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'reddit-stream')
    
    # Producer Settings
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '10'))
    STREAM_DELAY = int(os.getenv('STREAM_DELAY', '1'))  # seconds between batches