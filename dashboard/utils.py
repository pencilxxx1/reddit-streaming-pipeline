"""
Utility functions for the dashboard
"""
from datetime import datetime, timedelta
import pandas as pd

def get_time_series_data(collection, hours=24):
    """
    Get time series data for the last N hours
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    pipeline = [
        {
            '$match': {
                'processed_at': {'$gte': start_time, '$lte': end_time}
            }
        },
        {
            '$group': {
                '_id': {
                    '$dateToString': {
                        'format': '%Y-%m-%d %H:00',
                        'date': '$processed_at'
                    }
                },
                'count': {'$sum': 1}
            }
        },
        {'$sort': {'_id': 1}}
    ]
    
    result = list(collection.aggregate(pipeline))
    return pd.DataFrame(result)

def get_sentiment_distribution(collection):
    """
    Get sentiment distribution
    """
    pipeline = [
        {
            '$group': {
                '_id': '$sentiment_label',
                'count': {'$sum': 1}
            }
        }
    ]
    
    result = list(collection.aggregate(pipeline))
    return pd.DataFrame(result)

def get_top_subreddits(collection, limit=10):
    """
    Get top subreddits by post count
    """
    pipeline = [
        {
            '$group': {
                '_id': '$subreddit',
                'count': {'$sum': 1},
                'avg_score': {'$avg': '$score'}
            }
        },
        {'$sort': {'count': -1}},
        {'$limit': limit}
    ]
    
    result = list(collection.aggregate(pipeline))
    return pd.DataFrame(result)