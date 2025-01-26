from flask import Flask, request, redirect
import os

app = Flask(__name__)

@app.route('/')
def handle_callback():
    code = request.args.get('code')
    if code:
        # Here you would typically exchange this code for an access token
        print(f"Authorization code received: {code}")
        
        # For simplicity, we'll return the code in the response
        return f"Authorization code received: {code}. You can close this window.", 200
    else:
        return "No code received.", 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
