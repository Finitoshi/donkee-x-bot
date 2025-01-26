import tweepy
import requests
import json
import os
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Grok API Key
GROK_API_KEY = os.environ.get('GROK_API_KEY')
if not GROK_API_KEY:
    logger.error("GROK_API_KEY is not set in the environment")
    raise ValueError("GROK_API_KEY is required")

GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# OAuth 2.0 Credentials
client_id = os.environ.get('X_CLIENT_ID')
client_secret = os.environ.get('X_CLIENT_SECRET')
access_token = os.environ.get('X_ACCESS_TOKEN')
refresh_token = os.environ.get('X_REFRESH_TOKEN')

if not all([client_id, access_token, refresh_token]):
    logger.error("Required OAuth 2.0 credentials are missing from the environment")
    exit(1)

def refresh_access_token():
    """Refreshes the access token using the refresh token."""
    token_url = "https://api.x.com/2/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id
    }
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code == 200:
        token_data = response.json()
        new_access_token = token_data.get('access_token')
        new_refresh_token = token_data.get('refresh_token')  # New refresh token if provided
        if new_refresh_token:
            os.environ['X_REFRESH_TOKEN'] = new_refresh_token
        return new_access_token
    else:
        logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
        return None

def generate_tweet_with_grok():
    """Generates a tweet using Grok AI."""
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
    """Posts a tweet to X, refreshing the access token if necessary."""
    global access_token
    try:
        client = tweepy.Client(bearer_token=access_token)
        response = client.create_tweet(text=message)
        logger.info(f"Successfully posted tweet: {message[:50]}...")
        return True
    except tweepy.TweepError as e:
        if 'expired' in str(e):
            new_token = refresh_access_token()
            if new_token:
                access_token = new_token
                logger.info("Access token refreshed.")
                return post_tweet(message)  # Try posting again with the new token
        logger.error(f"Tweepy Error: {e}")
        return False

if __name__ == "__main__":
    tweet = generate_tweet_with_grok()
    if tweet and post_tweet(tweet):
        logger.info("Tweet posted successfully.")
    else:
        logger.info("Failed to post tweet.")
