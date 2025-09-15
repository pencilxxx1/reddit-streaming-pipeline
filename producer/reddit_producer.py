"""
Reddit Producer - Streams Reddit data to Kafka
This script connects to Reddit API using PRAW and streams posts/comments to Kafka
"""
import json
import time
import logging
from datetime import datetime
import praw
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RedditProducer:
    """
    Handles Reddit API connection and streams data to Kafka
    """
    
    def __init__(self):
        """Initialize Reddit and Kafka connections"""
        self.config = Config()
        self.reddit = None
        self.kafka_producer = None
        self._connect_reddit()
        self._connect_kafka()
    
    def _connect_reddit(self):
        """Establish connection to Reddit API using PRAW"""
        try:
            self.reddit = praw.Reddit(
                client_id=self.config.REDDIT_CLIENT_ID,
                client_secret=self.config.REDDIT_CLIENT_SECRET,
                user_agent=self.config.REDDIT_USER_AGENT
            )
            # Test connection
            _ = self.reddit.user.me()
            logger.info("Successfully connected to Reddit API")
        except Exception as e:
            logger.error(f"Failed to connect to Reddit: {e}")
            raise
    
    def _connect_kafka(self):
        """Establish connection to Kafka broker"""
        max_retries = 10
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.kafka_producer = KafkaProducer(
                    bootstrap_servers=[self.config.KAFKA_BROKER],
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None,
                    acks='all',  # Wait for all replicas to acknowledge
                    retries=5,
                    max_in_flight_requests_per_connection=1
                )
                logger.info(f"Connected to Kafka broker at {self.config.KAFKA_BROKER}")
                return
            except NoBrokersAvailable:
                retry_count += 1
                logger.warning(f"Kafka not ready, retrying... ({retry_count}/{max_retries})")
                time.sleep(5)
        
        raise Exception("Failed to connect to Kafka after maximum retries")
    
    def _process_submission(self, submission):
        """
        Process a Reddit submission and extract relevant fields
        
        Args:
            submission: PRAW Submission object
            
        Returns:
            dict: Processed submission data
        """
        return {
            'type': 'submission',
            'id': submission.id,
            'title': submission.title,
            'author': str(submission.author) if submission.author else '[deleted]',
            'subreddit': str(submission.subreddit),
            'text': submission.selftext,
            'url': submission.url,
            'score': submission.score,
            'num_comments': submission.num_comments,
            'created_utc': submission.created_utc,
            'timestamp': datetime.utcnow().isoformat(),
            'over_18': submission.over_18,
            'upvote_ratio': submission.upvote_ratio,
            'permalink': f"https://reddit.com{submission.permalink}"
        }
    
    def _process_comment(self, comment):
        """
        Process a Reddit comment and extract relevant fields
        
        Args:
            comment: PRAW Comment object
            
        Returns:
            dict: Processed comment data
        """
        return {
            'type': 'comment',
            'id': comment.id,
            'body': comment.body,
            'author': str(comment.author) if comment.author else '[deleted]',
            'subreddit': str(comment.subreddit),
            'score': comment.score,
            'created_utc': comment.created_utc,
            'timestamp': datetime.utcnow().isoformat(),
            'parent_id': comment.parent_id,
            'permalink': f"https://reddit.com{comment.permalink}"
        }
    
    def stream_submissions(self):
        """
        Stream new submissions from specified subreddits
        """
        logger.info(f"Starting submission stream for subreddits: {self.config.REDDIT_SUBREDDITS}")
        
        for subreddit_name in self.config.REDDIT_SUBREDDITS:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Stream new submissions
                for submission in subreddit.stream.submissions(skip_existing=True):
                    try:
                        # Process submission
                        data = self._process_submission(submission)
                        
                        # Send to Kafka
                        self.kafka_producer.send(
                            self.config.KAFKA_TOPIC,
                            key=f"submission_{submission.id}",
                            value=data
                        )
                        
                        logger.info(f"Sent submission {submission.id} to Kafka")
                        
                    except Exception as e:
                        logger.error(f"Error processing submission {submission.id}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error streaming from r/{subreddit_name}: {e}")
                continue
    
    def stream_comments(self):
        """
        Stream new comments from specified subreddits
        """
        logger.info(f"Starting comment stream for subreddits: {self.config.REDDIT_SUBREDDITS}")
        
        for subreddit_name in self.config.REDDIT_SUBREDDITS:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Stream new comments
                for comment in subreddit.stream.comments(skip_existing=True):
                    try:
                        # Process comment
                        data = self._process_comment(comment)
                        
                        # Send to Kafka
                        self.kafka_producer.send(
                            self.config.KAFKA_TOPIC,
                            key=f"comment_{comment.id}",
                            value=data
                        )
                        
                        logger.info(f"Sent comment {comment.id} to Kafka")
                        
                    except Exception as e:
                        logger.error(f"Error processing comment {comment.id}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error streaming comments from r/{subreddit_name}: {e}")
                continue
    
    def run(self):
        """
        Main execution loop - streams both submissions and comments
        """
        import threading
        
        try:
            # Create threads for parallel streaming
            submission_thread = threading.Thread(target=self.stream_submissions)
            comment_thread = threading.Thread(target=self.stream_comments)
            
            # Start threads
            submission_thread.start()
            comment_thread.start()
            
            # Wait for threads to complete (they won't in normal operation)
            submission_thread.join()
            comment_thread.join()
            
        except KeyboardInterrupt:
            logger.info("Shutting down producer...")
        finally:
            if self.kafka_producer:
                self.kafka_producer.flush()
                self.kafka_producer.close()
            logger.info("Producer shutdown complete")

if __name__ == "__main__":
    producer = RedditProducer()
    producer.run()