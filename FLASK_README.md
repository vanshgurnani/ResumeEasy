# Resume Analyzer - Flask Web Application

A modern, AI-powered resume analysis tool with a beautiful web interface built with Flask and Tailwind CSS.

## 🌟 Features

- **Modern Web Interface**: Beautiful, responsive UI built with Tailwind CSS and Alpine.js
- **AI-Powered Analysis**: Extract and analyze resume data using Google Gemini AI
- **Multiple File Formats**: Support for PDF, DOCX, TXT, and image files
- **Interactive Chat**: Ask questions about your resume data
- **Interview Preparation**: Generate customized interview questions
- **Export Functionality**: Format and export your resume data
- **Real-time Processing**: Drag-and-drop file upload with progress indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Required Python packages (see requirements.txt)

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   FLASK_DEBUG=True
   PORT=5000
   ```

4. **Run the application**:
   ```bash
   python run_flask_app.py
   ```

   Or directly:
   ```bash
   python flask_app.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
├── flask_app.py              # Main Flask application
├── run_flask_app.py          # Application runner script
├── templates/
│   └── resume_analyzer.html  # Modern web interface
├── resume_extractor.py       # AI resume analysis logic
├── file_processor.py         # File processing utilities
├── uploads/                  # Uploaded files directory
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables (create this)
```

## 🎯 Usage Guide

### 1. Upload Resume
- **Drag and drop** your resume file onto the upload area
- Or **click "Choose File"** to select from your computer
- Supported formats: PDF, DOCX, TXT, JPG, PNG, BMP, TIFF

### 2. View Analysis
After upload, you'll see:
- **Personal Information**: Name, email, phone, location
- **Skills**: Technical and soft skills categorized
- **Work Experience**: Job history with responsibilities
- **Education**: Academic background

### 3. Interactive Features

#### Chat with Resume
- Click **"Chat with Resume"** button
- Ask questions like:
  - "What are my strongest technical skills?"
  - "How can I improve my resume for software roles?"
  - "What projects should I highlight?"

#### Interview Preparation
- Click **"Interview Prep"** button
- Optionally specify a job role
- Get customized interview questions based on your background

#### Export Options
- Click **"Export PDF"** to get a formatted version
- Download or share your analyzed resume data

## 🔧 API Endpoints

The Flask application provides RESTful API endpoints:

### Upload & Analysis
- `POST /api/upload` - Upload and analyze resume
- `GET /api/session/<session_id>` - Get session data

### Interactive Features
- `POST /api/chat` - Chat about resume data
- `POST /api/interview-prep` - Generate interview questions
- `POST /api/export-pdf` - Export formatted resume

### Utility
- `GET /api/health` - Health check
- `GET /api/sessions` - List active sessions

## 🎨 Design Features

### Modern UI Components
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Drag & Drop**: Intuitive file upload experience
- **Modal Windows**: Clean chat and interview prep interfaces
- **Toast Notifications**: Real-time feedback for user actions
- **Loading States**: Visual feedback during processing

### Color Scheme
- **Primary**: Blue (#3B82F6) - Main actions and highlights
- **Secondary**: Green (#10B981) - Success states and chat
- **Accent**: Orange (#F59E0B) - Interview prep and warnings
- **Purple**: Export and advanced features

## 🔒 Security Features

- **File Type Validation**: Only allowed file extensions
- **File Size Limits**: Maximum 16MB upload size
- **Session Management**: Secure session handling
- **Input Sanitization**: Protected against common vulnerabilities

## 🛠️ Development

### Running in Development Mode
```bash
export FLASK_DEBUG=True
python flask_app.py
```

### Adding New Features
1. **Backend**: Add new routes in `flask_app.py`
2. **Frontend**: Update `templates/resume_analyzer.html`
3. **Styling**: Use Tailwind CSS classes for consistent design

### Environment Variables
- `GEMINI_API_KEY`: Required - Your Google Gemini API key
- `FLASK_SECRET_KEY`: Optional - Flask session secret
- `FLASK_DEBUG`: Optional - Enable debug mode
- `PORT`: Optional - Server port (default: 5000)

## 📊 Comparison: Telegram Bot vs Flask App

| Feature | Telegram Bot | Flask Web App |
|---------|--------------|---------------|
| **Interface** | Chat-based | Modern web UI |
| **File Upload** | Telegram native | Drag & drop |
| **Accessibility** | Mobile-friendly | Cross-platform |
| **User Experience** | Conversational | Visual & intuitive |
| **Sharing** | Telegram required | Direct web links |
| **Customization** | Limited | Highly customizable |

## 🚨 Troubleshooting

### Common Issues

1. **"Missing GEMINI_API_KEY"**
   - Create `.env` file with your API key
   - Ensure the key is valid and active

2. **File Upload Fails**
   - Check file size (max 16MB)
   - Verify file format is supported
   - Ensure uploads/ directory exists

3. **Chat Not Working**
   - Verify resume was uploaded successfully
   - Check console for JavaScript errors
   - Ensure API endpoints are accessible

4. **Styling Issues**
   - Check internet connection (CDN dependencies)
   - Clear browser cache
   - Verify Tailwind CSS is loading

## 🔄 Migration from Telegram Bot

If you're migrating from the Telegram bot:

1. **Data**: No data migration needed (stateless)
2. **Features**: All bot features available in web interface
3. **API Keys**: Same Gemini API key works for both
4. **Deployment**: Can run both simultaneously

## 📝 License

This project uses the same license as the original Telegram bot implementation.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Enjoy your new modern resume analyzer web application! 🎉**