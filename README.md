# Resume Extractor Telegram Bot

A powerful Telegram bot that extracts and analyzes resume information using AI, and can generate a beautiful PDF resume using a modern HTML template.

## Features

- 🤖 **AI-Powered Analysis**: Uses Google Gemini 2.0 Flash for intelligent resume parsing
- 📄 **Multiple File Formats**: Supports PDF, DOCX, TXT, and image files
- 🔍 **Comprehensive Extraction**: Extracts personal info, experience, education, skills, projects, achievements, and more
- 💬 **Interactive Chat**: Chat with AI about the analyzed resume for insights and advice
- 🎯 **Interview Preparation Agent**: Comprehensive interview prep with personalized questions and strategies
- 📱 **Easy to Use**: Simple Telegram interface with inline keyboards
- 🔒 **Privacy Focused**: Files are processed temporarily and deleted after analysis
- 📊 **Structured Output**: Returns both formatted text and raw JSON data (for chat/interview, not stored locally)
- 📝 **PDF Generation**: Use `/convert` to generate a modern PDF resume from your data using Playwright

## Folder Structure

```
ResumeEasy/
│
├── telegram_bot.py            # Main Telegram bot logic
├── resume_extractor.py        # Resume extraction and AI integration
├── file_processor.py          # File handling and text extraction
├── index.html                 # HTML template for PDF generation
├── requirements.txt           # Python dependencies
├── main.py                    # Entry point for running the bot
├── app.py                     # (Optional) Flask API
├── resume_jsons/              # (Used for temp files and PDF generation only)
├── README.md
└── ...
```

## PDF Generation with Playwright

- The `/convert` command allows users to upload a resume and receive a PDF generated from a modern HTML template.
- **No JSON files are stored** for analysis; only temporary files are used for PDF generation.
- Playwright (headless Chromium) is used for accurate HTML-to-PDF rendering.

### Playwright Setup

1. **Install Playwright:**
   ```bash
   pip install playwright
   python -m playwright install
   ```
2. **If deploying on Linux/Render,** ensure you run `python -m playwright install` as part of your build or startup process.

## Usage

1. **Start the bot:**
   ```bash
   python main.py
   ```
2. **On Telegram:**
   - Send `/start` to begin
   - Upload a resume file for analysis (PDF, DOCX, TXT, or image)
   - Use `/convert` and upload a resume to receive a PDF generated from your data

## Data Mapping & Template

- The bot expects resume data in a structured JSON format, with fields like `personal_info`, `education`, `experience`, `skills`, `projects`, and `achievements`.
- The HTML template (`index.html`) uses placeholders for all these sections, ensuring your PDF is fully populated.
- See the template for details on how your data is mapped.

## Privacy & Security

- Files are processed in temporary storage and deleted immediately after analysis or PDF generation.
- No personal data is stored permanently.

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
