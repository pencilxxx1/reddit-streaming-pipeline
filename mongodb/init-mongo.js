// Initialize MongoDB database and collections
db = db.getSiblingDB('reddit_data');

// Create collections
db.createCollection('processed_posts');
db.createCollection('analytics_summary');

// Create indexes for better performance
db.processed_posts.createIndex({ "timestamp": -1 });
db.processed_posts.createIndex({ "type": 1 });
db.processed_posts.createIndex({ "subreddit": 1 });
db.processed_posts.createIndex({ "sentiment_label": 1 });
db.processed_posts.createIndex({ "author": 1 });
db.processed_posts.createIndex({ "score": -1 });

// Create compound indexes
db.processed_posts.createIndex({ "subreddit": 1, "timestamp": -1 });
db.processed_posts.createIndex({ "sentiment_label": 1, "timestamp": -1 });

print("MongoDB initialization complete");