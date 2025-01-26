# initial_token_setup.py
# This script should be run once to get the initial OAuth tokens for the bot.

import tweepy
import requests
import json
import os
import logging
import base64
import hashlib
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

client_id = os.environ.get('X_CLIENT_ID')
client_secret = os.environ.get('X_CLIENT_SECRET')
redirect_uri = os.environ.get('X_REDIRECT_URI', 'https://your-render-service-name.onrender.com/')

def generate_code_verifier():
    # Generate a random code verifier for PKCE
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
    return code_verifier

def generate_code_challenge(code_verifier):
    # Generate code challenge from code verifier for PKCE
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).decode('utf-8').rstrip('=')
    return code_challenge

def get_initial_tokens():
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    
    # Construct the authorize URL for user to authorize the app
    authorize_url = f"https://x.com/i/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=tweet.write&code_challenge={code_challenge}&code_challenge_method=S256"
    print(f"Please visit this URL to authorize the app: {authorize_url}")
    
    # Wait for user to input the authorization code after manually authorizing via the Render service
    auth_code = input("Enter the authorization code you received from your Render service: ")

    token_url = "https://api.x.com/2/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
        "client_id": client_id
    }
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get('access_token'), token_data.get('refresh_token')
    else:
        logger.error(f"Failed to get initial tokens: {response.status_code} - {response.text}")
        return None, None

if __name__ == "__main__":
    access_token, refresh_token = get_initial_tokens()
    if access_token and refresh_token:
        # Save tokens in environment variables for use by the main script
        os.environ['X_ACCESS_TOKEN'] = access_token
        os.environ['X_REFRESH_TOKEN'] = refresh_token
        logger.info("Tokens saved successfully. Now you can use these in your environment.")
    else:
        logger.error("Failed to get tokens.")
