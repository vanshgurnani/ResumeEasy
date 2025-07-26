#!/usr/bin/env python3
"""
Flask API for Resume Extractor - Web Interface
Converts Telegram bot functionality to web-based API endpoints
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv
import tempfile
import uuid

from resume_extractor import ResumeExtractor
from file_processor import FileProcessor

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
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'bmp', 'tiff'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize extractors
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("Missing GEMINI_API_KEY environment variable")

resume_extractor = ResumeExtractor(gemini_api_key)
file_processor = FileProcessor()

# Store user sessions for chat functionality
user_sessions = {}  # session_id -> {'resume_data': {...}, 'chat_history': [...]}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """Get file type from filename."""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return None

async def process_uploaded_file(file_path: str, file_type: str) -> Optional[str]:
    """Process uploaded file and extract text content."""
    try:
        if file_type == 'pdf':
            return await file_processor.extract_text_from_pdf(file_path)
        elif file_type == 'docx':
            return await file_processor.extract_text_from_docx(file_path)
        elif file_type == 'txt':
            return await file_processor.extract_text_from_txt(file_path)
        elif file_type in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
            # OCR functionality would go here
            return "OCR functionality coming soon for image files"
        else:
            return None
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return None

@app.route('/')
def index():
    """Main page with file upload interface."""
    return render_template('resume_analyzer.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Resume Extractor API is running',
        'version': '1.0.0'
    })

@app.route('/api/upload', methods=['POST'])
def upload_resume():
    """Upload and analyze resume file."""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported'}), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(file_path)
        
        # Get file type
        file_type = get_file_type(filename)
        
        # Process file asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            text_content = loop.run_until_complete(process_uploaded_file(file_path, file_type))
        finally:
            loop.close()
        
        if not text_content:
            # Clean up file
            os.remove(file_path)
            return jsonify({'error': 'Failed to extract text from file'}), 400
        
        # Extract resume data
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            resume_data = loop.run_until_complete(resume_extractor.extract_resume_info(text_content))
        finally:
            loop.close()
        
        if not resume_data:
            # Clean up file
            os.remove(file_path)
            return jsonify({'error': 'Failed to analyze resume'}), 500
        
        # Store in session
        user_sessions[session_id] = {
            'resume_data': resume_data,
            'chat_history': [],
            'file_path': file_path,
            'filename': filename
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'resume_data': resume_data,
            'message': 'Resume analyzed successfully!'
        })
        
    except Exception as e:
        logger.error(f"Error in upload_resume: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_resume():
    """Chat about the analyzed resume."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        session_id = session.get('session_id') or data.get('session_id')
        if not session_id or session_id not in user_sessions:
            return jsonify({'error': 'No resume session found. Please upload a resume first.'}), 400
        
        user_message = data['message']
        session_data = user_sessions[session_id]
        resume_data = session_data['resume_data']
        
        # Generate AI response
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(resume_extractor.chat_about_resume(user_message, resume_data))
        finally:
            loop.close()
        
        # Store in chat history
        session_data['chat_history'].append({
            'user': user_message,
            'bot': response,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'response': response,
            'chat_history': session_data['chat_history']
        })
        
    except Exception as e:
        logger.error(f"Error in chat_with_resume: {e}")
        return jsonify({'error': 'Failed to process chat message'}), 500

@app.route('/api/interview-prep', methods=['POST'])
def interview_preparation():
    """Generate comprehensive interview preparation."""
    try:
        data = request.get_json()
        session_id = session.get('session_id') or (data.get('session_id') if data else None)
        
        if not session_id or session_id not in user_sessions:
            return jsonify({'error': 'No resume session found. Please upload a resume first.'}), 400
        
        session_data = user_sessions[session_id]
        resume_data = session_data['resume_data']
        
        # Generate interview preparation
        job_role = data.get('job_role', 'Software Developer') if data else 'Software Developer'
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            prep_data = loop.run_until_complete(resume_extractor.interview_preparation(resume_data, job_role))
            # Format the interview data for display
            formatted_prep = resume_extractor.format_interview_preparation(prep_data)
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'interview_prep': formatted_prep
        })
        
    except Exception as e:
        logger.error(f"Error in interview_preparation: {e}")
        return jsonify({'error': 'Failed to generate interview preparation'}), 500

@app.route('/api/export-pdf', methods=['POST'])
def export_resume_pdf():
    """Export formatted resume as PDF."""
    try:
        data = request.get_json()
        session_id = session.get('session_id') or (data.get('session_id') if data else None)
        
        if not session_id or session_id not in user_sessions:
            return jsonify({'error': 'No resume session found. Please upload a resume first.'}), 400
        
        session_data = user_sessions[session_id]
        resume_data = session_data['resume_data']
        
        # Generate formatted resume
        formatted_resume = resume_extractor.format_extracted_info(resume_data)
        
        return jsonify({
            'success': True,
            'formatted_resume': formatted_resume,
            'download_url': f'/api/download-pdf/{session_id}'
        })
        
    except Exception as e:
        logger.error(f"Error in export_resume_pdf: {e}")
        return jsonify({'error': 'Failed to export PDF'}), 500

@app.route('/api/session/<session_id>')
def get_session_data(session_id):
    """Get session data for a specific session."""
    try:
        if session_id not in user_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = user_sessions[session_id]
        return jsonify({
            'success': True,
            'resume_data': session_data['resume_data'],
            'chat_history': session_data['chat_history'],
            'filename': session_data['filename']
        })
        
    except Exception as e:
        logger.error(f"Error in get_session_data: {e}")
        return jsonify({'error': 'Failed to retrieve session data'}), 500

@app.route('/api/sessions')
def list_sessions():
    """List all active sessions (for demo purposes)."""
    try:
        sessions = []
        for session_id, data in user_sessions.items():
            sessions.append({
                'session_id': session_id,
                'filename': data['filename'],
                'name': data['resume_data'].get('personal_info', {}).get('name', 'Unknown'),
                'chat_count': len(data['chat_history'])
            })
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
        
    except Exception as e:
        logger.error(f"Error in list_sessions: {e}")
        return jsonify({'error': 'Failed to list sessions'}), 500

@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    import datetime
    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask Resume Extractor API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)