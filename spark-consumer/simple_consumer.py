import os
import json
from datetime import datetime
from pymongo import MongoClient

# Direct MongoDB connection test
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['reddit_data']
collection = db['processed_posts']

# Test insert
test_doc = {
    'type': 'test',
    'title': 'Pipeline Test',
    'processed_at': datetime.utcnow(),
    'sentiment_label': 'positive'
}

result = collection.insert_one(test_doc)
print(f"Inserted: {result.inserted_id}")
print(f"Total documents: {collection.count_documents({})}")