#!/usr/bin/env python3
"""
Simple Flask API to control Resume Extractor Telegram Bot with Threading Support
"""

import os
import time
import threading
import asyncio
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from telegram_bot import ResumeTelegramBot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global bot management
class SimpleBotManager:
    def __init__(self):
        self.bot = None
        self.bot_thread = None
        self.running = False
        self.loop = None

    def is_running(self):
        return self.running and self.bot_thread and self.bot_thread.is_alive()

bot_manager = SimpleBotManager()

@app.route('/')
def home():
    return jsonify({
        "message": "Simple Resume Extractor Bot API",
        "endpoints": ["/start", "/stop", "/status", "/health"]
    })

def _run_bot_thread():
    """Run bot in separate thread with proper event loop handling."""
    try:
        logger.info("Starting bot in thread...")
        bot_manager.running = True

        # Check if running in cloud environment
        is_cloud = os.getenv('RENDER') or os.getenv('DYNO') or os.getenv('CLOUD_DEPLOYMENT', '').lower() == 'true'

        if is_cloud:
            logger.info("Cloud environment detected, using cloud-safe execution...")
            _run_bot_cloud_safe()
        else:
            logger.info("Local environment detected, using standard execution...")
            _run_bot_local()

    except Exception as e:
        logger.error(f"Bot thread error: {e}")
        bot_manager.running = False
    finally:
        # Cleanup
        if hasattr(bot_manager, 'loop') and bot_manager.loop and not bot_manager.loop.is_closed():
            try:
                bot_manager.loop.close()
            except Exception as cleanup_error:
                logger.warning(f"Event loop cleanup error: {cleanup_error}")

def _run_bot_local():
    """Run bot for local development."""
    try:
        # Create new event loop for this thread
        bot_manager.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(bot_manager.loop)

        # Run the bot
        bot_manager.bot.run()

    except Exception as e:
        logger.error(f"Local bot execution error: {e}")
        raise

def _run_bot_cloud_safe():
    """Run bot with cloud deployment safety measures."""
    try:
        # Create new event loop for this thread
        bot_manager.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(bot_manager.loop)

        # Run async bot execution
        bot_manager.loop.run_until_complete(_async_bot_execution())

    except Exception as e:
        logger.error(f"Cloud bot execution error: {e}")
        # Fallback to sync execution
        logger.info("Falling back to synchronous execution...")
        try:
            bot_manager.bot.run()
        except Exception as fallback_error:
            logger.error(f"Fallback execution failed: {fallback_error}")
            raise

async def _async_bot_execution():
    """Async bot execution for cloud environments."""
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

        # Create application
        application = Application.builder().token(bot_manager.bot.bot_token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", bot_manager.bot.start_command))
        application.add_handler(CommandHandler("help", bot_manager.bot.help_command))
        application.add_handler(CommandHandler("about", bot_manager.bot.about_command))
        application.add_handler(CommandHandler("chat", bot_manager.bot.chat_command))
        application.add_handler(CommandHandler("interview", bot_manager.bot.interview_command))
        application.add_handler(CommandHandler("stop", bot_manager.bot.stop_command))
        application.add_handler(MessageHandler(filters.Document.ALL, bot_manager.bot.handle_document))
        application.add_handler(CallbackQueryHandler(bot_manager.bot.handle_callback_query))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_manager.bot.handle_text_message))

        # Store application reference
        bot_manager.bot.application = application

        # Initialize and start
        await application.initialize()
        await application.start()

        # Start polling with cloud settings
        await application.updater.start_polling(
            poll_interval=2.0,
            timeout=30,
            bootstrap_retries=5,
            read_timeout=60,
            write_timeout=60,
            connect_timeout=60,
            pool_timeout=60,
            stop_signals=None
        )

        logger.info("Bot is running and polling...")

        # Keep running
        while bot_manager.running:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Async bot execution error: {e}")
        raise
    finally:
        # Cleanup
        try:
            if hasattr(bot_manager.bot, 'application') and bot_manager.bot.application:
                await bot_manager.bot.application.updater.stop()
                await bot_manager.bot.application.stop()
                await bot_manager.bot.application.shutdown()
        except Exception as cleanup_error:
            logger.warning(f"Bot cleanup error: {cleanup_error}")

@app.route('/start', methods=['GET'])
def start_bot():
    if bot_manager.is_running():
        return jsonify({"status": "error", "message": "Bot already running"}), 400

    try:
        # Create bot instance
        bot_manager.bot = ResumeTelegramBot()

        # Start bot in separate thread
        bot_manager.bot_thread = threading.Thread(target=_run_bot_thread, daemon=True)
        bot_manager.bot_thread.start()

        # Wait a moment to check if started successfully
        time.sleep(2)

        if bot_manager.is_running():
            return jsonify({"status": "success", "message": "Bot started successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Bot failed to start"}), 500

    except Exception as e:
        logger.error(f"Error starting bot: {e}")
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
