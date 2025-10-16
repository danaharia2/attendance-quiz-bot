# app.py - HTTP server untuk health checks
from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def health_check():
    return "🤖 Bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    # Ini akan dihandle oleh main.py nanti
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)