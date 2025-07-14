#!/usr/bin/env python3
"""
Flask API for controlling the Resume Extractor Telegram Bot
"""

import os
import threading
import time
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import asyncio
from telegram_bot import ResumeTelegramBot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables to manage bot state
bot_instance = None
bot_thread = None
bot_running = False

class BotManager:
    """Manages the Telegram bot lifecycle."""
    
    def __init__(self):
        self.bot = None
        self.thread = None
        self.running = False
        self.loop = None
    
    def start_bot(self):
        """Start the Telegram bot in a separate thread."""
        if self.running:
            return {"status": "error", "message": "Bot is already running"}
        
        try:
            # Create bot instance
            self.bot = ResumeTelegramBot()
            
            # Start bot in a separate thread
            self.thread = threading.Thread(target=self._run_bot, daemon=True)
            self.thread.start()
            
            # Wait a moment to check if bot started successfully
            time.sleep(2)
            
            if self.running:
                return {"status": "success", "message": "Bot started successfully"}
            else:
                return {"status": "error", "message": "Failed to start bot"}
                
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            return {"status": "error", "message": f"Failed to start bot: {str(e)}"}
    
    def _run_bot(self):
        """Run the bot in the thread with proper async event loop."""
        try:
            self.running = True
            logger.info("Starting Telegram bot...")

            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Run the bot
            self.bot.run()

        except Exception as e:
            logger.error(f"Bot error: {e}")
            self.running = False
        finally:
            # Clean up the event loop
            if self.loop and not self.loop.is_closed():
                self.loop.close()
    
    def stop_bot(self):
        """Stop the Telegram bot."""
        if not self.running:
            return {"status": "error", "message": "Bot is not running"}

        try:
            self.running = False

            # Try to stop the bot gracefully
            if self.bot and hasattr(self.bot, 'application'):
                try:
                    # Schedule the stop in the bot's event loop
                    if self.loop and not self.loop.is_closed():
                        asyncio.run_coroutine_threadsafe(
                            self.bot.application.stop(),
                            self.loop
                        )
                except Exception as stop_error:
                    logger.warning(f"Could not gracefully stop bot: {stop_error}")

            return {"status": "success", "message": "Bot stop signal sent"}
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            return {"status": "error", "message": f"Failed to stop bot: {str(e)}"}
    
    def get_status(self):
        """Get bot status."""
        return {
            "status": "success",
            "data": {
                "running": self.running,
                "thread_alive": self.thread.is_alive() if self.thread else False,
                "bot_instance": self.bot is not None
            }
        }

# Global bot manager
bot_manager = BotManager()

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information."""
    return jsonify({
        "message": "Resume Extractor Telegram Bot API",
        "version": "1.0.0",
        "endpoints": {
            "/start": "POST - Start the Telegram bot",
            "/stop": "POST - Stop the Telegram bot", 
            "/status": "GET - Get bot status",
            "/health": "GET - Health check"
        },
        "bot_features": [
            "Resume extraction from PDF, DOCX, TXT files",
            "AI-powered analysis using Gemini 2.0 Flash",
            "Interactive chat about resumes",
            "Comprehensive interview preparation",
            "Multiple interview types support"
        ]
    })

@app.route('/start', methods=['GET'])
def start_bot():
    """Start the Telegram bot."""
    try:
        result = bot_manager.start_bot()
        
        if result["status"] == "success":
            return jsonify({
                "status": "success",
                "message": "Telegram bot started successfully",
                "data": {
                    "bot_running": True,
                    "timestamp": time.time()
                }
            }), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in start_bot endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to start bot: {str(e)}"
        }), 500

@app.route('/stop', methods=['POST'])
def stop_bot():
    """Stop the Telegram bot."""
    try:
        result = bot_manager.stop_bot()
        
        if result["status"] == "success":
            return jsonify({
                "status": "success",
                "message": "Telegram bot stop signal sent",
                "data": {
                    "bot_running": False,
                    "timestamp": time.time()
                }
            }), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in stop_bot endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to stop bot: {str(e)}"
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get the current status of the Telegram bot."""
    try:
        result = bot_manager.get_status()
        
        return jsonify({
            "status": "success",
            "message": "Bot status retrieved",
            "data": {
                **result["data"],
                "timestamp": time.time(),
                "api_version": "1.0.0"
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_status endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get status: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "Flask API is running",
        "data": {
            "api_running": True,
            "bot_running": bot_manager.running,
            "timestamp": time.time(),
            "environment": {
                "telegram_token_configured": bool(os.getenv('TELEGRAM_BOT_TOKEN')),
                "gemini_key_configured": bool(os.getenv('GEMINI_API_KEY'))
            }
        }
    }), 200

@app.route('/config', methods=['GET'])
def get_config():
    """Get configuration status (without exposing sensitive data)."""
    return jsonify({
        "status": "success",
        "message": "Configuration status",
        "data": {
            "telegram_bot_token": "configured" if os.getenv('TELEGRAM_BOT_TOKEN') else "missing",
            "gemini_api_key": "configured" if os.getenv('GEMINI_API_KEY') else "missing",
            "required_env_vars": ["TELEGRAM_BOT_TOKEN", "GEMINI_API_KEY"],
            "supported_file_types": [".pdf", ".docx", ".txt", ".jpg", ".jpeg", ".png"],
            "features": [
                "Resume extraction and analysis",
                "Interactive chat mode",
                "Interview preparation agent",
                "Multiple interview types",
                "JSON data export"
            ]
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "available_endpoints": ["/", "/start", "/stop", "/status", "/health", "/config"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "details": str(error)
    }), 500

if __name__ == '__main__':
    # Check environment variables
    if not os.getenv('TELEGRAM_BOT_TOKEN') or not os.getenv('GEMINI_API_KEY'):
        logger.warning("Missing required environment variables. Check TELEGRAM_BOT_TOKEN and GEMINI_API_KEY")
        print("⚠️  Warning: Missing required environment variables")
        print("Please ensure TELEGRAM_BOT_TOKEN and GEMINI_API_KEY are set in your .env file")
    
    # Start Flask app
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting Flask API on port {port}")
    print(f"📱 Use POST /start to launch the Telegram bot")
    print(f"📊 Use GET /status to check bot status")
    print(f"🏥 Use GET /health for health checks")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
