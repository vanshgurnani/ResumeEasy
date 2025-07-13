# Resume Extractor Telegram Bot

A powerful Telegram bot that extracts and analyzes resume information using Google's Gemini 2.0 Flash AI model.

## Features

- 🤖 **AI-Powered Analysis**: Uses Google Gemini 2.0 Flash for intelligent resume parsing
- 📄 **Multiple File Formats**: Supports PDF, DOCX, TXT, and image files
- 🔍 **Comprehensive Extraction**: Extracts personal info, experience, education, skills, projects, and more
- 💬 **Interactive Chat**: Chat with AI about the analyzed resume for insights and advice
- 🎯 **Interview Preparation Agent**: Comprehensive interview prep with personalized questions and strategies
- 📱 **Easy to Use**: Simple Telegram interface with inline keyboards
- 🔒 **Privacy Focused**: Files are processed temporarily and deleted after analysis
- 📊 **Structured Output**: Returns both formatted text and raw JSON data

## Supported File Formats

- **PDF** (.pdf) - Full text extraction
- **Word Document** (.docx) - Text and table extraction
- **Text File** (.txt) - Direct text processing
- **Images** (.jpg, .jpeg, .png, .bmp, .tiff) - OCR support (coming soon)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd resumeChat
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your Telegram Bot Token and Gemini API Key:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Getting API Keys

### Telegram Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command to create a new bot
3. Follow the instructions and get your bot token

### Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key to your `.env` file

## Usage

1. **Start the bot**:
   ```bash
   python telegram_bot.py
   ```

2. **Run the application**:

   **Option A: Direct Telegram Bot**
   ```bash
   python telegram_bot.py
   ```

   **Option B: Flask API (Recommended)**
   ```bash
   # Development mode
   python run_api.py development

   # Production mode with Gunicorn
   python run_api.py production
   ```

3. **Use the bot on Telegram**:
   - Find your bot on Telegram
   - Send `/start` to begin
   - Upload a resume file
   - Get structured analysis results
   - Use `/chat` or click "Chat About Resume" to start interactive chat
   - Use `/interview` or click "Interview Preparation" for comprehensive interview prep
   - Ask questions about the resume and get AI-powered insights

## Bot Commands

- `/start` - Welcome message and instructions
- `/help` - Detailed usage guide
- `/about` - Information about the bot
- `/chat` - Enable chat mode to discuss the analyzed resume
- `/interview` - Get comprehensive interview preparation based on resume
- `/stop` - Exit chat mode and return to normal operation

## Extracted Information

The bot extracts the following information from resumes:

### Personal Information
- Full name
- Email address
- Phone number
- Location
- LinkedIn profile
- GitHub profile
- Portfolio website

### Professional Details
- Work experience with companies, positions, and responsibilities
- Education history with institutions, degrees, and dates
- Technical and soft skills
- Programming languages and tools
- Projects with descriptions and technologies
- Certifications and achievements

## Interactive Chat Feature

After analyzing a resume, you can engage in an interactive chat with the AI to:

### Ask Questions About the Resume
- "What are the candidate's strongest skills?"
- "Tell me about their work experience"
- "What programming languages do they know?"
- "What's their educational background?"

### Get Career Advice
- "How can this resume be improved?"
- "What career paths would suit this candidate?"
- "What skills should they develop next?"
- "How competitive is this candidate for senior roles?"

### Resume Enhancement Suggestions
- "What sections are missing from this resume?"
- "How can the work experience section be improved?"
- "What keywords should be added for ATS optimization?"
- "How can this resume stand out more?"

### Interview Preparation
- "What interview questions might be asked based on this resume?"
- "What are the candidate's potential weaknesses?"
- "How should they present their experience?"

## 🎯 Interview Preparation Agent

The Interview Preparation Agent is a comprehensive feature that creates personalized interview preparation guides based on the analyzed resume.

### Interview Types Supported

#### 🏢 General Interview
- Overall interview preparation covering all aspects
- Balanced mix of behavioral, technical, and situational questions
- General career advice and presentation tips

#### 💻 Technical Interview
- Focus on technical skills and programming knowledge
- Coding challenges and system design questions
- Deep-dive technical preparation based on resume skills

#### 👔 Behavioral Interview
- STAR method scenarios from work experience
- Soft skills and personality-based questions
- Leadership and teamwork examples

#### 🎯 Leadership Interview
- Management and leadership scenarios
- Strategic thinking and decision-making questions
- Team building and conflict resolution

### What You Get

#### 📝 Likely Interview Questions
- Personalized questions based on your specific experience
- Categorized by type (behavioral, technical, situational)
- Suggested answer approaches and key points to cover

#### 💪 Strengths to Highlight
- Key strengths identified from your resume
- Specific evidence and examples to support each strength
- How to articulate and present these strengths effectively

#### ⚠️ Potential Weaknesses & Mitigation
- Areas that might raise concerns for interviewers
- Strategies to address and reframe potential weaknesses
- How to turn challenges into growth opportunities

#### 🔧 Technical Preparation
- Deep-dive questions for each technical skill
- Preparation tips for technical assessments
- How to demonstrate technical expertise

#### 📖 STAR Method Scenarios
- Situation, Task, Action, Result examples from your experience
- Ready-to-use stories for behavioral questions
- How to structure compelling narratives

#### 🤔 Questions to Ask Interviewers
- Thoughtful questions that demonstrate interest and research
- Role-specific and company-specific inquiries
- Questions that help you evaluate the opportunity

#### 💰 Salary Negotiation Guidance
- Market range estimates based on your experience level
- Negotiation points that justify higher compensation
- How to approach salary discussions professionally

### How to Use

1. **Analyze your resume** first using the bot
2. **Use `/interview`** command or click "Interview Preparation"
3. **Select interview type** that matches your upcoming interview
4. **Review the comprehensive guide** generated specifically for you
5. **Download detailed JSON** for offline study and practice
6. **Practice your answers** using the provided scenarios and questions

## 🌐 Flask API Endpoints

The Flask API provides HTTP endpoints to control the Telegram bot programmatically:

### Base URL
```
http://localhost:5000
```

### Available Endpoints

#### `GET /`
- **Description**: API information and available endpoints
- **Response**: JSON with API details and bot features

#### `POST /start`
- **Description**: Start the Telegram bot
- **Response**: Success/error status with bot running state
- **Example**:
  ```bash
  curl -X POST http://localhost:5000/start
  ```

#### `POST /stop`
- **Description**: Stop the Telegram bot
- **Response**: Success/error status with bot stopped state
- **Example**:
  ```bash
  curl -X POST http://localhost:5000/stop
  ```

#### `GET /status`
- **Description**: Get current bot status
- **Response**: Bot running state and thread information
- **Example**:
  ```bash
  curl http://localhost:5000/status
  ```

#### `GET /health`
- **Description**: Health check for the API and bot
- **Response**: API health status and environment configuration
- **Example**:
  ```bash
  curl http://localhost:5000/health
  ```

#### `GET /config`
- **Description**: Get configuration status (without sensitive data)
- **Response**: Environment variables status and supported features

### API Response Format

All endpoints return JSON responses in this format:
```json
{
  "status": "success|error",
  "message": "Description of the result",
  "data": {
    // Additional response data
  }
}
```

### Running the API

**Development Mode:**
```bash
python run_api.py development
```

**Production Mode with Gunicorn:**
```bash
python run_api.py production
```

**Environment Variables:**
```bash
FLASK_PORT=5000          # API port (default: 5000)
FLASK_DEBUG=False        # Debug mode (default: False)
GUNICORN_WORKERS=2       # Number of Gunicorn workers (default: 2)
RUN_MODE=production      # Run mode (development/production)
```

## File Structure

```
resumeChat/
├── telegram_bot.py          # Main bot application
├── resume_extractor.py      # Gemini AI integration for resume parsing
├── file_processor.py        # File handling and text extraction
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Error Handling

The bot includes comprehensive error handling for:
- Unsupported file formats
- File size limits (20MB max)
- API failures
- Text extraction errors
- JSON parsing issues

## Privacy & Security

- Files are processed in temporary storage and deleted immediately after analysis
- No personal data is stored permanently
- All processing happens server-side with secure API calls

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:
1. Check the logs for error messages
2. Ensure your API keys are correctly configured
3. Verify file formats are supported
4. Contact the development team

## Future Enhancements

- [ ] OCR support for image files
- [ ] Batch processing multiple resumes
- [ ] Resume comparison features
- [ ] Export to different formats
- [ ] Advanced filtering and search
- [ ] Integration with HR systems
