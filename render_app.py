#!/usr/bin/env python3
"""
Render-optimized entry point for Resume Extractor Telegram Bot
This file is specifically designed to work with Render's deployment environment
"""

import os
import sys
import logging
import signal
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set cloud deployment flag
os.environ['CLOUD_DEPLOYMENT'] = 'true'

# Configure logging for cloud deployment
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['TELEGRAM_BOT_TOKEN', 'GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("All required environment variables are set")
    return True

def run_bot_only():
    """Run only the Telegram bot (for simple deployment)."""
    try:
        from telegram_bot import ResumeTelegramBot
        
        logger.info("Starting Telegram bot in direct mode...")
        bot = ResumeTelegramBot()
        bot.run()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)

def run_with_flask():
    """Run Flask API with bot management (for full API deployment)."""
    try:
        from main import app, bot_manager
        
        # Auto-start the bot
        logger.info("Auto-starting Telegram bot...")
        result = bot_manager.start_bot()
        
        if result["status"] == "success":
            logger.info("Bot started successfully")
        else:
            logger.warning(f"Bot start warning: {result['message']}")
        
        # Start Flask app
        port = int(os.getenv('PORT', 5000))  # Render uses PORT env var
        logger.info(f"Starting Flask API on port {port}")
        
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
        sys.exit(1)

def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

def main():
    """Main entry point for Render deployment."""
    logger.info("🚀 Starting Resume Extractor for Render deployment")
    
    # Set up signal handlers
    setup_signal_handlers()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Determine run mode
    run_mode = os.getenv('RUN_MODE', 'flask').lower()
    
    logger.info(f"Run mode: {run_mode}")
    
    if run_mode == 'bot':
        # Run only the Telegram bot
        run_bot_only()
    elif run_mode == 'flask':
        # Run Flask API with bot management
        run_with_flask()
    else:
        logger.error(f"Invalid run mode: {run_mode}. Use 'bot' or 'flask'")
        sys.exit(1)

if __name__ == '__main__':
    main()
