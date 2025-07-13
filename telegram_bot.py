import os
import logging
import asyncio
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode
import tempfile
from dotenv import load_dotenv

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

class ResumeTelegramBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')

        if not self.bot_token or not self.gemini_api_key:
            raise ValueError("Missing required environment variables. Check TELEGRAM_BOT_TOKEN and GEMINI_API_KEY")

        self.resume_extractor = ResumeExtractor(self.gemini_api_key)
        self.file_processor = FileProcessor()

        # Store user states for chat mode
        self.user_states = {}  # user_id -> {'mode': 'chat', 'resume_data': {...}}
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        # Reset user state
        user_id = update.effective_user.id
        self.user_states[user_id] = {'mode': 'normal', 'resume_data': None}

        welcome_message = """
🤖 **Welcome to Resume Extractor Bot!**

I can help you extract and analyze information from resumes.

**Supported file formats:**
📄 PDF (.pdf)
📝 Word Document (.docx)
📃 Text File (.txt)
🖼️ Images (.jpg, .jpeg, .png, .bmp, .tiff) - OCR coming soon

**How to use:**
1. Send me a resume file
2. I'll extract key information like:
   • Personal details
   • Work experience
   • Education
   • Skills
   • Projects
   • Certifications
3. **NEW!** Chat with me about the resume after analysis

**Commands:**
/start - Show this welcome message
/help - Get help and usage instructions
/about - Learn more about this bot
/chat - Enable chat mode (after resume analysis)
/interview - Get comprehensive interview preparation
/stop - Exit chat mode

Just upload your resume file and I'll get started! 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("📖 Help", callback_data="help")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
📚 **How to Use Resume Extractor Bot**

**Step 1:** Upload your resume file
• Supported formats: PDF, DOCX, TXT, Images
• File size limit: 20MB

**Step 2:** Wait for processing
• The bot will extract text from your file
• AI will analyze and structure the information

**Step 3:** Review extracted information
• Personal information
• Work experience
• Education details
• Skills and technologies
• Projects and achievements

**Step 4:** Interactive Features (NEW!)
• Use /chat to enable chat mode for Q&A
• Use /interview for comprehensive interview prep
• Ask questions about your resume
• Get career advice and suggestions
• Request resume improvements
• Use /stop to exit interactive modes

**Tips for best results:**
✅ Use clear, well-formatted resumes
✅ Ensure text is readable (not blurry images)
✅ Include complete information in your resume

**Privacy:**
🔒 Files are processed temporarily and deleted after analysis
🔒 No personal data is stored permanently

Need more help? Contact the developer!
        """
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command."""
        about_message = """
🤖 **About Resume Extractor Bot**

**Technology Stack:**
• 🧠 Google Gemini 2.0 Flash AI
• 🐍 Python with python-telegram-bot
• 📄 PyPDF2 for PDF processing
• 📝 python-docx for Word documents

**Features:**
• Intelligent resume parsing
• Structured data extraction
• Multiple file format support
• Fast processing with AI

**Version:** 1.0.0
**Developer:** Resume Bot Team

This bot helps recruiters, HR professionals, and job seekers quickly extract and analyze resume information using advanced AI technology.

**Feedback & Support:**
Found a bug or have suggestions? We'd love to hear from you!
        """
        
        await update.message.reply_text(about_message, parse_mode=ParseMode.MARKDOWN)

    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chat command to enable chat mode."""
        user_id = update.effective_user.id
        user_state = self.user_states.get(user_id, {})

        if not user_state.get('resume_data'):
            await update.message.reply_text(
                "❌ No resume data found. Please upload and analyze a resume first before starting chat mode.\n\n"
                "Upload a resume file to get started!"
            )
            return

        self.user_states[user_id]['mode'] = 'chat'

        keyboard = [[InlineKeyboardButton("🚪 Exit Chat Mode", callback_data="exit_chat")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "💬 **Chat Mode Enabled!**\n\n"
            "You can now ask me questions about the analyzed resume. For example:\n"
            "• What are the key skills?\n"
            "• How can I improve this resume?\n"
            "• What career advice do you have?\n"
            "• Tell me about the work experience\n\n"
            "Use /stop or click the button below to exit chat mode.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command to exit chat mode."""
        user_id = update.effective_user.id

        if user_id in self.user_states:
            self.user_states[user_id]['mode'] = 'normal'

        await update.message.reply_text(
            "🚪 **Chat mode disabled.**\n\n"
            "You can upload a new resume file or use /chat to re-enable chat mode.",
            parse_mode=ParseMode.MARKDOWN
        )

    async def interview_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /interview command for interview preparation."""
        user_id = update.effective_user.id
        user_state = self.user_states.get(user_id, {})

        if not user_state.get('resume_data'):
            await update.message.reply_text(
                "❌ No resume data found. Please upload and analyze a resume first before getting interview preparation.\n\n"
                "Upload a resume file to get started!"
            )
            return

        # Show interview type selection
        keyboard = [
            [InlineKeyboardButton("🏢 General Interview", callback_data="interview_general")],
            [InlineKeyboardButton("💻 Technical Interview", callback_data="interview_technical")],
            [InlineKeyboardButton("👔 Behavioral Interview", callback_data="interview_behavioral")],
            [InlineKeyboardButton("🎯 Leadership Interview", callback_data="interview_leadership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🎯 **Interview Preparation Agent**\n\n"
            "Select the type of interview you're preparing for:\n\n"
            "🏢 **General** - Overall interview preparation\n"
            "💻 **Technical** - Focus on technical skills and coding\n"
            "👔 **Behavioral** - STAR method and soft skills\n"
            "🎯 **Leadership** - Management and leadership scenarios\n\n"
            "I'll create a comprehensive preparation guide based on your resume!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document uploads."""
        document = update.message.document
        
        if not document:
            await update.message.reply_text("❌ No document received. Please try again.")
            return
        
        # Check file size (20MB limit)
        if document.file_size > 20 * 1024 * 1024:
            await update.message.reply_text("❌ File too large. Please upload files smaller than 20MB.")
            return
        
        # Check file extension
        if not self.file_processor.is_supported_file(document.file_name):
            supported = ", ".join(self.file_processor.get_supported_extensions())
            await update.message.reply_text(
                f"❌ Unsupported file format.\n\nSupported formats: {supported}"
            )
            return
        
        # Send processing message
        processing_msg = await update.message.reply_text("🔄 Processing your resume... Please wait.")
        
        try:
            # Download file
            file = await context.bot.get_file(document.file_id)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(document.file_name)[1]) as temp_file:
                temp_file_path = temp_file.name
                await file.download_to_drive(temp_file_path)
            
            # Extract text from file
            file_extension = os.path.splitext(document.file_name)[1]
            extracted_text = await self.file_processor.process_file(temp_file_path, file_extension)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            if not extracted_text:
                await processing_msg.edit_text("❌ Failed to extract text from the file. Please try a different file.")
                return
            
            if len(extracted_text.strip()) < 50:
                await processing_msg.edit_text("❌ The file appears to contain very little text. Please check your file and try again.")
                return
            
            # Update processing message
            await processing_msg.edit_text("🧠 Analyzing resume with AI... Almost done!")
            
            # Extract resume information using Gemini
            extracted_info = await self.resume_extractor.extract_resume_info(extracted_text)
            
            # Format and send results
            formatted_result = self.resume_extractor.format_extracted_info(extracted_info)
            
            await processing_msg.edit_text(formatted_result, parse_mode=ParseMode.MARKDOWN)
            
            # Store resume data for chat functionality
            user_id = update.effective_user.id
            self.user_states[user_id] = {
                'mode': 'normal',
                'resume_data': extracted_info
            }

            # Offer additional options
            keyboard = [
                [InlineKeyboardButton("💬 Chat About Resume", callback_data="start_chat")],
                [InlineKeyboardButton("🎯 Interview Preparation", callback_data="start_interview")],
                [InlineKeyboardButton("📋 Get Raw JSON Data", callback_data=f"json_{update.message.message_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "✅ Resume analysis complete! You can now:\n"
                "• 💬 Chat with me about the resume\n"
                "• 🎯 Get comprehensive interview preparation\n"
                "• 📋 Export raw JSON data\n"
                "• 📄 Upload another resume",
                reply_markup=reply_markup
            )

            # Store extracted data for potential JSON export
            context.user_data[f"json_{update.message.message_id}"] = extracted_info
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            await processing_msg.edit_text(f"❌ An error occurred while processing your resume: {str(e)}")

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "help":
            await self.help_command(update, context)
        elif query.data == "about":
            await self.about_command(update, context)
        elif query.data == "start_chat":
            user_id = update.effective_user.id
            if user_id in self.user_states and self.user_states[user_id].get('resume_data'):
                self.user_states[user_id]['mode'] = 'chat'

                keyboard = [[InlineKeyboardButton("🚪 Exit Chat Mode", callback_data="exit_chat")]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.message.reply_text(
                    "💬 **Chat Mode Enabled!**\n\n"
                    "Ask me anything about the analyzed resume!\n\n"
                    "Examples:\n"
                    "• What are the key skills?\n"
                    "• How can I improve this resume?\n"
                    "• What career advice do you have?\n"
                    "• Tell me about the work experience",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            else:
                await query.message.reply_text("❌ No resume data found. Please analyze a resume first.")
        elif query.data == "exit_chat":
            user_id = update.effective_user.id
            if user_id in self.user_states:
                self.user_states[user_id]['mode'] = 'normal'

            await query.message.reply_text(
                "🚪 **Chat mode disabled.**\n\n"
                "You can upload a new resume file or click 'Chat About Resume' to re-enable chat mode.",
                parse_mode=ParseMode.MARKDOWN
            )
        elif query.data == "start_interview":
            user_id = update.effective_user.id
            if user_id in self.user_states and self.user_states[user_id].get('resume_data'):
                # Show interview type selection
                keyboard = [
                    [InlineKeyboardButton("🏢 General Interview", callback_data="interview_general")],
                    [InlineKeyboardButton("💻 Technical Interview", callback_data="interview_technical")],
                    [InlineKeyboardButton("👔 Behavioral Interview", callback_data="interview_behavioral")],
                    [InlineKeyboardButton("🎯 Leadership Interview", callback_data="interview_leadership")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.message.reply_text(
                    "🎯 **Interview Preparation Agent**\n\n"
                    "Select the type of interview you're preparing for:\n\n"
                    "🏢 **General** - Overall interview preparation\n"
                    "💻 **Technical** - Focus on technical skills and coding\n"
                    "👔 **Behavioral** - STAR method and soft skills\n"
                    "🎯 **Leadership** - Management and leadership scenarios",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            else:
                await query.message.reply_text("❌ No resume data found. Please analyze a resume first.")
        elif query.data.startswith("interview_"):
            interview_type = query.data.replace("interview_", "")
            user_id = update.effective_user.id
            user_state = self.user_states.get(user_id, {})

            if not user_state.get('resume_data'):
                await query.message.reply_text("❌ No resume data found. Please analyze a resume first.")
                return

            # Send processing message
            processing_msg = await query.message.reply_text("🎯 Generating your personalized interview preparation guide... Please wait.")

            try:
                # Generate interview preparation
                interview_data = await self.resume_extractor.interview_preparation(
                    user_state['resume_data'],
                    interview_type
                )

                # Format and send results
                formatted_result = self.resume_extractor.format_interview_preparation(interview_data)

                await processing_msg.edit_text(formatted_result, parse_mode=ParseMode.MARKDOWN)

                # Offer to get detailed JSON data
                keyboard = [
                    [InlineKeyboardButton("📋 Get Detailed Interview Guide", callback_data=f"interview_json_{query.message.message_id}")],
                    [InlineKeyboardButton("🔄 Try Different Interview Type", callback_data="start_interview")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.message.reply_text(
                    "✅ Interview preparation complete!\n\n"
                    "💡 **Pro tip**: Practice your answers out loud and prepare specific examples from your experience!",
                    reply_markup=reply_markup
                )

                # Store interview data for detailed export
                context.user_data[f"interview_json_{query.message.message_id}"] = interview_data

            except Exception as e:
                logger.error(f"Error generating interview preparation: {e}")
                await processing_msg.edit_text(f"❌ An error occurred while generating interview preparation: {str(e)}")
        elif query.data.startswith("interview_json_"):
            message_id = query.data.replace("interview_json_", "")
            interview_data = context.user_data.get(f"interview_json_{message_id}")

            if interview_data:
                import json
                json_text = json.dumps(interview_data, indent=2, ensure_ascii=False)

                # Send as file since it will be long
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
                    temp_file.write(json_text)
                    temp_file_path = temp_file.name

                await query.message.reply_document(
                    document=open(temp_file_path, 'rb'),
                    filename="interview_preparation_guide.json",
                    caption="🎯 Here's your detailed interview preparation guide in JSON format"
                )
                os.unlink(temp_file_path)
            else:
                await query.message.reply_text("❌ Interview data not found. Please generate interview preparation first.")
        elif query.data.startswith("json_"):
            message_id = query.data.replace("json_", "")
            json_data = context.user_data.get(f"json_{message_id}")
            
            if json_data:
                import json
                json_text = json.dumps(json_data, indent=2, ensure_ascii=False)
                
                # Send as file if too long
                if len(json_text) > 4000:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
                        temp_file.write(json_text)
                        temp_file_path = temp_file.name
                    
                    await query.message.reply_document(
                        document=open(temp_file_path, 'rb'),
                        filename="resume_data.json",
                        caption="📋 Here's your resume data in JSON format"
                    )
                    os.unlink(temp_file_path)
                else:
                    await query.message.reply_text(f"```json\n{json_text}\n```", parse_mode=ParseMode.MARKDOWN)
            else:
                await query.message.reply_text("❌ JSON data not found. Please process a resume first.")

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages - either chat or regular messages."""
        user_id = update.effective_user.id
        user_state = self.user_states.get(user_id, {})

        # Check if user is in chat mode
        if user_state.get('mode') == 'chat' and user_state.get('resume_data'):
            # Process chat message
            user_question = update.message.text
            resume_data = user_state['resume_data']

            # Send typing indicator
            await update.message.chat.send_action(action="typing")

            try:
                # Get AI response about the resume
                ai_response = await self.resume_extractor.chat_about_resume(user_question, resume_data)

                keyboard = [[InlineKeyboardButton("🚪 Exit Chat Mode", callback_data="exit_chat")]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    f"🤖 {ai_response}",
                    reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Error in chat response: {e}")
                await update.message.reply_text(
                    "❌ Sorry, I encountered an error while processing your question. Please try again."
                )
        else:
            # Regular message - ask for resume upload
            await update.message.reply_text(
                "📄 Please send me a resume file (PDF, DOCX, TXT, or image) to analyze.\n\n"
                "Use /help for more information about supported formats.\n\n"
                "If you've already analyzed a resume, use /chat to start chatting about it!"
            )

    def run(self):
        """Start the bot."""
        application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("about", self.about_command))
        application.add_handler(CommandHandler("chat", self.chat_command))
        application.add_handler(CommandHandler("interview", self.interview_command))
        application.add_handler(CommandHandler("stop", self.stop_command))
        application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        logger.info("Starting Resume Extractor Bot...")
        application.run_polling()

if __name__ == "__main__":
    try:
        bot = ResumeTelegramBot()
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"Error: {e}")
        print("Please check your environment variables and try again.")
