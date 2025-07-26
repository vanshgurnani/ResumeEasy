#!/usr/bin/env python3
"""
Script to run the Flask Resume Analyzer application
"""

import os
import sys
from dotenv import load_dotenv

def setup_environment():
    """Setup environment variables and check dependencies."""
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ['GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with the following variables:")
        print("GEMINI_API_KEY=your_gemini_api_key_here")
        print("FLASK_SECRET_KEY=your_secret_key_here  # Optional")
        print("FLASK_DEBUG=True  # Optional")
        print("PORT=5000  # Optional")
        return False
    
    return True

def main():
    """Main function to run the Flask app."""
    print("🚀 Starting Resume Analyzer Flask Application...")
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    print("✅ Environment variables loaded successfully")
    
    # Import and run Flask app
    try:
        from flask_app import app
        
        # Get configuration
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        print(f"📱 Starting server on http://localhost:{port}")
        print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
        print("\n" + "="*50)
        print("🎯 Resume Analyzer Features:")
        print("   • Upload resume files (PDF, DOCX, TXT, Images)")
        print("   • AI-powered resume analysis")
        print("   • Chat with your resume data")
        print("   • Interview preparation questions")
        print("   • Export formatted resume")
        print("="*50 + "\n")
        
        # Run the Flask application
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()