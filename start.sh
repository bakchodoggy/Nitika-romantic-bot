#!/bin/sh
# Start FastAPI API on port 8080 in the background
uvicorn stars_payment:app --host 0.0.0.0 --port 8080 &
# Start your Telegram bot runner
python3 bot_runner.py