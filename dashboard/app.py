"""
Streamlit Dashboard for Reddit Stream Analytics
Real-time visualization of processed Reddit data
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from utils import get_time_series_data, get_sentiment_distribution, get_top_subreddits

# Page configuration
st.set_page_config(
    page_title="Reddit Stream Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# MongoDB connection
@st.cache_resource
def init_connection():
    """Initialize MongoDB connection"""
    return MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF4500;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🔴 Reddit Stream Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Initialize connection
    client = init_connection()
    db = client[os.getenv('MONGO_DATABASE', 'reddit_data')]
    collection = db['processed_posts']
    
    # Sidebar filters
    st.sidebar.header("📊 Filters")
    
    # Time range filter
    time_range = st.sidebar.selectbox(
        "Time Range",
        ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days", "All Time"]
    )
    
    # Calculate time filter
    now = datetime.utcnow()
    if time_range == "Last Hour":
        time_filter = now - timedelta(hours=1)
    elif time_range == "Last 6 Hours":
        time_filter = now - timedelta(hours=6)
    elif time_range == "Last 24 Hours":
        time_filter = now - timedelta(hours=24)
    elif time_range == "Last 7 Days":
        time_filter = now - timedelta(days=7)
    else:
        time_filter = None
    
    # Post type filter
    post_type = st.sidebar.multiselect(
        "Post Type",
        ["submission", "comment"],
        default=["submission", "comment"]
    )
    
    # Sentiment filter
    sentiment_filter = st.sidebar.multiselect(
        "Sentiment",
        ["positive", "neutral", "negative"],
        default=["positive", "neutral", "negative"]
    )
    
    # Build query
    query = {}
    if time_filter:
        query['processed_at'] = {'$gte': time_filter}
    if post_type:
        query['type'] = {'$in': post_type}
    if sentiment_filter:
        query['sentiment_label'] = {'$in': sentiment_filter}
    
    # Fetch data
    total_posts = collection.count_documents(query)
    recent_posts = list(collection.find(query).sort('processed_at', -1).limit(1000))
    
    if recent_posts:
        df = pd.DataFrame(recent_posts)
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Total Posts", f"{total_posts:,}")
        
        with col2:
            avg_score = df['score'].mean() if 'score' in df else 0
            st.metric("⭐ Avg Score", f"{avg_score:.1f}")
        
        with col3:
            positive_pct = (df['sentiment_label'] == 'positive').mean() * 100
            st.metric("😊 Positive %", f"{positive_pct:.1f}%")
        
        with col4:
            unique_subreddits = df['subreddit'].nunique() if 'subreddit' in df else 0
            st.metric("🌐 Subreddits", unique_subreddits)
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment Distribution
            st.subheader("😊 Sentiment Distribution")
            sentiment_counts = df['sentiment_label'].value_counts()
            fig_sentiment = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                color_discrete_map={
                    'positive': '#00cc00',
                    'neutral': '#ffcc00',
                    'negative': '#ff0000'
                }
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            # Top Subreddits
            st.subheader("🏆 Top Subreddits")
            top_subreddits = df['subreddit'].value_counts().head(10)
            fig_subreddits = px.bar(
                x=top_subreddits.values,
                y=top_subreddits.index,
                orientation='h',
                labels={'x': 'Posts', 'y': 'Subreddit'}
            )
            st.plotly_chart(fig_subreddits, use_container_width=True)
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            # Time Series
            st.subheader("📈 Activity Over Time")
            df['hour'] = pd.to_datetime(df['processed_at']).dt.floor('H')
            time_series = df.groupby('hour').size().reset_index(name='count')
            fig_time = px.line(
                time_series,
                x='hour',
                y='count',
                labels={'hour': 'Time', 'count': 'Posts'}
            )
            st.plotly_chart(fig_time, use_container_width=True)
        
        with col2:
            # Language Distribution
            st.subheader("🌍 Language Distribution")
            if 'language' in df:
                lang_counts = df['language'].value_counts().head(10)
                fig_lang = px.bar(
                    x=lang_counts.index,
                    y=lang_counts.values,
                    labels={'x': 'Language', 'y': 'Count'}
                )
                st.plotly_chart(fig_lang, use_container_width=True)
        
        # Word Cloud
        st.subheader("☁️ Word Cloud")
        if 'cleaned_text' in df and not df['cleaned_text'].empty:
            text = ' '.join(df['cleaned_text'].dropna())
            if text:
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
        
        # Recent Posts Table
        st.subheader("📋 Recent Posts")
        display_df = df[['type', 'subreddit', 'sentiment_label', 'score', 'processed_at']].head(20)
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.warning("No data available for the selected filters. Waiting for data to stream...")
    
    # Auto-refresh
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto Refresh (10s)")
    if auto_refresh:
        import time
        time.sleep(10)
        st.rerun()

if __name__ == "__main__":
    main()