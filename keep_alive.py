import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "💖 Nitika bot is alive and flirting! 💖"

def run():
    try:
        port = int(os.getenv("PORT", 8080))  # Use environment variable for port
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Error starting server: {str(e)}")

def keep_alive():
    t = Thread(target=run, daemon=True)  # Ensures background thread stops safely
    t.start()