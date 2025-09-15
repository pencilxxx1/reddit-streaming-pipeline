import praw
import os

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="test"
)

for submission in reddit.subreddit("AskReddit").new(limit=5):
    print(f"Title: {submission.title}")