#!/usr/bin/env python3
"""
Simple Flask API to control Resume Extractor Telegram Bot
"""

import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from telegram_bot import ResumeTelegramBot  # Assumes this is implemented

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global bot instance
bot = None
bot_running = False

@app.route('/')
def home():
    return jsonify({
        "message": "Simple Resume Extractor Bot API",
        "endpoints": ["/start", "/stop", "/status", "/health"]
    })

@app.route('/start', methods=['GET'])
def start_bot():
    global bot, bot_running
    if bot_running:
        return jsonify({"status": "error", "message": "Bot already running"}), 400

    try:
        bot = ResumeTelegramBot()
        bot.run()
        bot_running = True
        return jsonify({"status": "success", "message": "Bot started"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop_bot():
    global bot, bot_running
    if not bot_running:
        return jsonify({"status": "error", "message": "Bot not running"}), 400

    try:
        if hasattr(bot, 'application'):
            bot.application.stop()
        bot_running = False
        return jsonify({"status": "success", "message": "Bot stopped"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "success",
        "bot_running": bot_running,
        "timestamp": time.time()
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "bot_running": bot_running,
        "telegram_token_set": bool(os.getenv('TELEGRAM_BOT_TOKEN')),
        "gemini_key_set": bool(os.getenv('GEMINI_API_KEY'))
    }), 200

@app.errorhandler(404)
def not_found(_):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
