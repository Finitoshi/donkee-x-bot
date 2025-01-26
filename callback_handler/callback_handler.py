# callback_handler.py
# This Flask app handles OAuth callback from X

from flask import Flask, request
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def handle_callback():
    code = request.args.get('code')
    if code:
        logger.info(f"Authorization code received: {code}")
        return f"Authorization code received. You can close this window.", 200
    else:
        logger.warning("No code received in callback.")
        return "No code received.", 400

if __name__ == "__main__":
    # Use the PORT environment variable provided by Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
