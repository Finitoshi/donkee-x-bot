import tweepy
import requests
import json
import os
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OAuth 2.0 Credentials
client_id = os.environ.get('X_CLIENT_ID')
client_secret = os.environ.get('X_CLIENT_SECRET')

# Function to get bearer token using client credentials
def get_bearer_token():
    token_url = "https://api.twitter.com/2/oauth2/token"
    data = {
        "grant_type": "client_credentials"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }
    
    response = requests.post(token_url, auth=(client_id, client_secret), data=data, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        logger.error(f"Failed to get bearer token: {response.status_code} - {response.text}")
        return None

# Get the bearer token
bearer_token = get_bearer_token()

if not bearer_token:
    logger.error("Could not obtain bearer token. Exiting.")
    exit(1)

# Authentication - Using OAuth 2.0
client = tweepy.Client(bearer_token=bearer_token)

# Rest of your code remains similar, but use the new client for API calls
last_tweet_time = None

def generate_tweet_with_grok():
    # Your existing function...

def post_tweet(message):
    global last_tweet_time
    now = datetime.now()

    if last_tweet_time is None or now - last_tweet_time >= timedelta(hours=24):
        try:
            response = client.create_tweet(text=message)
            logger.info(f"Successfully posted tweet: {message[:50]}...")
            last_tweet_time = now
            return True
        except tweepy.errors.TweepyException as e:
            logger.error(f"Tweepy Error: {e}")
            return False
    else:
        time_left = timedelta(hours=24) - (now - last_tweet_time)
        logger.info(f"Waiting to post next tweet. Time left: {time_left}")
        return False

if __name__ == "__main__":
    tweet = generate_tweet_with_grok()
    if not post_tweet(tweet):
        logger.info("Tweet not posted due to rate limit.")
