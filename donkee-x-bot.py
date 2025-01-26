import tweepy
import requests
import json
import os
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Grok API Key - Use environment variables
GROK_API_KEY = os.environ.get('GROK_API_KEY')
if not GROK_API_KEY:
    logger.error("GROK_API_KEY is not set in the environment")
    raise ValueError("GROK_API_KEY is required")

GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# Use the bearer token directly from environment variables
bearer_token = os.environ.get('X_BEARER_TOKEN')
if not bearer_token:
    logger.error("X_BEARER_TOKEN is not set in the environment")
    exit(1)

# Authentication - Using OAuth 2.0 with the pre-existing bearer token
client = tweepy.Client(bearer_token=bearer_token)

# Track when the last tweet was posted to respect the 24-hour limit
last_tweet_time = None

def generate_tweet_with_grok():
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are DONKEE, a highly intelligent, edgy, weed-smoking donkey who loves Solana memecoins and degen trading. Your tweets should be witty, playful, and target Gen Z and Millennials. Avoid direct financial advice or promotions."
            },
            {
                "role": "user",
                "content": "Generate a tweet for me."
            }
        ],
        "model": "grok-2-latest",
        "stream": False,
        "temperature": 0.7
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GROK_API_KEY}'
    }

    try:
        response = requests.post(GROK_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        tweet_text = response_json['choices'][0]['message']['content']
        return tweet_text + " #ForEntertainmentOnly #NotFinancialAdvice"
    except requests.RequestException as e:
        logger.error(f"Failed to generate tweet with Grok: {e}")
        return "Error generating tweet"
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected response from Grok API: {e}")
        return "Error parsing Grok API response"

def post_tweet(message):
    global last_tweet_time
    now = datetime.now()

    # Check if 24 hours have passed since the last tweet
    if last_tweet_time is None or now - last_tweet_time >= timedelta(hours=24):
        try:
            response = client.create_tweet(text=message)
            logger.info(f"Successfully posted tweet: {message[:50]}...")
            last_tweet_time = now  # Update the last tweet time
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
