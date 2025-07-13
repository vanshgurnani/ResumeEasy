#!/usr/bin/env python3
"""
Setup script for Resume Extractor Telegram Bot
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def setup_environment():
    """Set up environment file."""
    print("🔧 Setting up environment...")
    
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            # Copy example file
            with open('.env.example', 'r') as example:
                content = example.read()
            
            with open('.env', 'w') as env_file:
                env_file.write(content)
            
            print("📝 Created .env file from template")
            print("⚠️  Please edit .env file and add your API keys:")
            print("   - TELEGRAM_BOT_TOKEN")
            print("   - GEMINI_API_KEY")
            return False
        else:
            print("❌ .env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
        return True

def check_api_keys():
    """Check if API keys are configured."""
    if not os.path.exists('.env'):
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    has_telegram_token = 'TELEGRAM_BOT_TOKEN=' in content and 'your_telegram_bot_token_here' not in content
    has_gemini_key = 'GEMINI_API_KEY=' in content and 'your_gemini_api_key_here' not in content
    
    if has_telegram_token and has_gemini_key:
        print("✅ API keys are configured")
        return True
    else:
        print("⚠️  Please configure your API keys in .env file:")
        if not has_telegram_token:
            print("   - Missing or invalid TELEGRAM_BOT_TOKEN")
        if not has_gemini_key:
            print("   - Missing or invalid GEMINI_API_KEY")
        return False

def main():
    """Main setup function."""
    print("🚀 Resume Extractor Bot Setup")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during package installation")
        return False
    
    print()
    
    # Setup environment
    env_ready = setup_environment()
    
    print()
    
    # Check API keys
    keys_ready = check_api_keys()
    
    print()
    print("=" * 40)
    
    if env_ready and keys_ready:
        print("✅ Setup completed successfully!")
        print("🎉 You can now run the bot with: python telegram_bot.py")
    else:
        print("⚠️  Setup partially completed")
        print("📝 Next steps:")
        print("   1. Edit .env file with your API keys")
        print("   2. Run: python telegram_bot.py")
    
    print()
    print("📚 Need help getting API keys?")
    print("   - Telegram Bot: https://t.me/botfather")
    print("   - Gemini API: https://makersuite.google.com/app/apikey")
    
    return True

if __name__ == "__main__":
    main()
