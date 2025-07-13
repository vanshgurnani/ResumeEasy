#!/usr/bin/env python3
"""
Simple startup script for the Resume Extractor Flask API
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all required packages are installed."""
    required_packages = [
        'flask',
        'flask_cors',
        'python-telegram-bot',
        'google-generativeai',
        'python-dotenv',
        'PyPDF2',
        'python-docx',
        'Pillow',
        'aiofiles'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['TELEGRAM_BOT_TOKEN', 'GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file")
        return False
    
    return True

def run_with_gunicorn():
    """Run the API with Gunicorn."""
    try:
        import gunicorn
    except ImportError:
        print("❌ Gunicorn not installed. Install with: pip install gunicorn")
        return False
    
    port = os.getenv('FLASK_PORT', '5000')
    workers = os.getenv('GUNICORN_WORKERS', '2')
    
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--workers', workers,
        '--timeout', '30',
        '--keepalive', '2',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--preload',
        '--access-logfile', '-',
        '--error-logfile', '-',
        'main:app'
    ]
    
    print(f"🚀 Starting with Gunicorn on port {port} with {workers} workers")
    print(f"📝 Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Gunicorn failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        return True

def run_development():
    """Run the API in development mode."""
    print("🔧 Starting in development mode...")
    
    try:
        from main import app
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        
        app.run(host='0.0.0.0', port=port, debug=debug)
        return True
    except Exception as e:
        print(f"❌ Failed to start development server: {e}")
        return False

def main():
    """Main function."""
    print("🤖 Resume Extractor Flask API Starter")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print("✅ All checks passed!")
    
    # Determine run mode
    mode = os.getenv('RUN_MODE', 'development').lower()
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    
    print(f"🎯 Run mode: {mode}")
    
    if mode in ['production', 'prod']:
        success = run_with_gunicorn()
    elif mode in ['development', 'dev']:
        success = run_development()
    else:
        print("❌ Invalid run mode. Use 'development' or 'production'")
        print("Usage: python start_api.py [development|production]")
        sys.exit(1)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
