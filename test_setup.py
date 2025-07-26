#!/usr/bin/env python3
"""
Test script to verify Flask Resume Analyzer setup
"""

import sys
import importlib

def test_imports():
    """Test that all required modules can be imported."""
    required_modules = [
        'flask',
        'flask_cors',
        'werkzeug',
        'google.generativeai',
        'python_dotenv',
        'PyPDF2',
        'docx',
        'PIL',
        'aiofiles',
        'asyncio'
    ]
    
    print("🔍 Testing module imports...")
    
    for module in required_modules:
        try:
            importlib.import_module(module.replace('-', '_'))
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module} - {e}")
            return False
    
    return True

def test_local_modules():
    """Test that local modules can be imported."""
    local_modules = [
        'resume_extractor',
        'file_processor'
    ]
    
    print("\n🔍 Testing local modules...")
    
    for module in local_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module} - {e}")
            return False
    
    return True

def test_flask_app():
    """Test that Flask app can be imported."""
    print("\n🔍 Testing Flask application...")
    
    try:
        from flask_app import app
        print("✅ Flask app imported successfully")
        
        # Test basic configuration
        if app.config.get('UPLOAD_FOLDER'):
            print("✅ Upload folder configured")
        else:
            print("⚠️  Upload folder not configured")
        
        return True
    except Exception as e:
        print(f"❌ Flask app import failed - {e}")
        return False

def test_environment():
    """Test environment setup."""
    import os
    from dotenv import load_dotenv
    
    print("\n🔍 Testing environment setup...")
    
    # Try to load .env file
    load_dotenv()
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found (optional)")
    
    # Check for required environment variable
    if os.getenv('GEMINI_API_KEY'):
        print("✅ GEMINI_API_KEY is set")
    else:
        print("❌ GEMINI_API_KEY not found")
        print("   Please set this in your .env file or environment")
        return False
    
    return True

def test_directories():
    """Test that required directories exist."""
    import os
    
    print("\n🔍 Testing directory structure...")
    
    required_dirs = ['templates', 'uploads']
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/ directory exists")
        else:
            print(f"❌ {directory}/ directory missing")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Created {directory}/ directory")
            except Exception as e:
                print(f"❌ Failed to create {directory}/ - {e}")
                return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Resume Analyzer Flask App Setup Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Local Modules", test_local_modules),
        ("Directory Structure", test_directories),
        ("Environment Variables", test_environment),
        ("Flask Application", test_flask_app),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! Your setup looks good.")
        print("\nTo start the application:")
        print("   python run_flask_app.py")
        print("   or")
        print("   python flask_app.py")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        print("\nCommon fixes:")
        print("   • Install dependencies: pip install -r requirements.txt")
        print("   • Create .env file with GEMINI_API_KEY")
        print("   • Check file permissions")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)