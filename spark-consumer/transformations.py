"""
Data transformation utilities for Spark processing
"""
from textblob import TextBlob
from langdetect import detect
import re

def clean_text(text):
    """
    Clean and preprocess text data
    
    Args:
        text (str): Raw text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.lower()

def analyze_sentiment(text):
    """
    Perform sentiment analysis on text
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Sentiment scores
    """
    if not text:
        return {
            'polarity': 0.0,
            'subjectivity': 0.0,
            'sentiment_label': 'neutral'
        }
    
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        # Classify sentiment
        if polarity > 0.1:
            label = 'positive'
        elif polarity < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'polarity': polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'sentiment_label': label
        }
    except:
        return {
            'polarity': 0.0,
            'subjectivity': 0.0,
            'sentiment_label': 'neutral'
        }

def detect_language(text):
    """
    Detect the language of text
    
    Args:
        text (str): Text to analyze
        
    Returns:
        str: Language code
    """
    if not text or len(text) < 10:
        return 'unknown'
    
    try:
        return detect(text)
    except:
        return 'unknown'

def extract_entities(text):
    """
    Extract named entities from text (simplified version)
    
    Args:
        text (str): Text to analyze
        
    Returns:
        list: Extracted entities
    """
    if not text:
        return []
    
    # Simple entity extraction using TextBlob
    try:
        blob = TextBlob(text)
        # Extract noun phrases as entities
        entities = list(blob.noun_phrases)
        return entities[:10]  # Limit to top 10 entities
    except:
        return []