#!/bin/bash
# start.sh - Startup script for Railway

echo "🚄 Starting Telegram Bot on Railway..."

# Install Python dependencies
pip install -r requirements.txt

# Start the bot
python main.py