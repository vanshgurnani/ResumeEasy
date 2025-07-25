# app.py
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
import asyncio
from resume_extractor import ResumeExtractor
from file_processor import FileProcessor
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import datetime

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")

resume_extractor = ResumeExtractor(GEMINI_API_KEY)
file_processor = FileProcessor()

# Helpers

def get_unique_path(suffix):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    return os.path.join('resume_jsons', f'resume_{timestamp}{suffix}')

def fill_html_template(resume_data: dict) -> str:
    pi = resume_data.get('personal_info', {})
    name = pi.get('name', '')
    email = pi.get('email', '')
    phone = pi.get('phone', '')
    location = pi.get('location', '')

    education_html = ''.join([
        f"<div><strong>{edu.get('institution')}</strong> ({edu.get('graduation_date')})<br>{edu.get('degree')} - GPA: {edu.get('gpa')}</div>"
        for edu in resume_data.get('education', [])
    ])

    experience_html = ''.join([
        f"<div><strong>{exp.get('company')}</strong> ({exp.get('duration')})<br>{exp.get('position')}<ul>{''.join([f'<li>{resp}</li>' for resp in exp.get('responsibilities', [])])}</ul></div>"
        for exp in resume_data.get('experience', [])
    ])

    projects_html = ''.join([
        f"<div><strong>{proj.get('name')}</strong><br>{proj.get('description')}<br>Tech: {', '.join(proj.get('technologies', []))}<br>URL: {proj.get('url')}</div>"
        for proj in resume_data.get('projects', [])
    ])

    achievements_html = ''.join([f"<li>{ach}</li>" for ach in resume_data.get('achievements', [])])

    skills_html = ''.join([
        f"<strong>{cat.title()}:</strong> {', '.join(items)}<br>"
        for cat, items in resume_data.get('skills', {}).items()
    ])

    return render_template('index.html', name=name, email=email, phone=phone, location=location,
                           education_section=education_html, experience_section=experience_html,
                           projects_section=projects_html, achievements_section=achievements_html,
                           skills_section=skills_html)

async def html_to_pdf_playwright(html_content, pdf_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)
        await page.pdf(path=pdf_path, format="A4")
        await browser.close()

@app.route('/')
def home():
    return render_template('index2.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1]

    if not file_processor.is_supported_file(filename):
        return jsonify({'error': f'Unsupported file type. Supported: {file_processor.get_supported_extensions()}'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    async def process_resume():
        extracted_text = await file_processor.process_file(file_path, ext)
        if not extracted_text:
            return jsonify({'error': 'Failed to extract text from file'}), 500

        resume_data = await resume_extractor.extract_resume_info(extracted_text)
        html_content = fill_html_template(resume_data)

        pdf_path = get_unique_path('.pdf')
        await html_to_pdf_playwright(html_content, pdf_path)

        return send_file(pdf_path, as_attachment=True, download_name='Converted_Resume.pdf')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(process_resume())

if __name__ == '__main__':
    app.run(debug=True)
