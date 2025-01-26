import tweepy
import time
import random
import requests
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# X API Credentials - Use environment variables
consumer_key = os.environ.get('X_CONSUMER_KEY')
consumer_secret = os.environ.get('X_CONSUMER_SECRET')
access_token = os.environ.get('X_ACCESS_TOKEN')
access_token_secret = os.environ.get('X_ACCESS_TOKEN_SECRET')

# Grok API Key - Use environment variables
GROK_API_KEY = os.environ.get('GROK_API_KEY')
if not GROK_API_KEY:
    logger.error("GROK_API_KEY is not set in the environment")
    raise ValueError("GROK_API_KEY is required")

GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

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
    try:
        api.update_status(message)
        logger.info(f"Successfully posted tweet: {message[:50]}...")
    except tweepy.TweepError as e:
        logger.error(f"Error posting tweet: {e.reason if hasattr(e, 'reason') else str(e)}")

def main():
    while True:
        tweet = generate_tweet_with_grok()
        post_tweet(tweet)

        # Sleep with some jitter to avoid exact hourly patterns
        sleep_time = 7200 + random.randint(-300, 300)  # 2 hours +/- 5 minutes
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
