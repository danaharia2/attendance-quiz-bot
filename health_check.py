# health_check.py
from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def health_check():
    return "🤖 Bot is healthy and running!", 200

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "running"}, 200

def run_health_server():
    port = int(os.environ.get('HEALTH_PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Jalankan health server di thread terpisah
health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()