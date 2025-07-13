import google.generativeai as genai
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ResumeExtractor:
    def __init__(self, api_key: str):
        """Initialize the resume extractor with Gemini API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def create_extraction_prompt(self) -> str:
        """Create a detailed prompt for resume extraction."""
        return """
        You are an expert resume parser. Extract the following information from the resume text and return it as a JSON object:

        {
            "personal_info": {
                "name": "Full name",
                "email": "Email address",
                "phone": "Phone number",
                "location": "City, State/Country",
                "linkedin": "LinkedIn profile URL",
                "github": "GitHub profile URL",
                "portfolio": "Portfolio website URL"
            },
            "summary": "Professional summary or objective",
            "experience": [
                {
                    "company": "Company name",
                    "position": "Job title",
                    "duration": "Start date - End date",
                    "location": "City, State",
                    "responsibilities": ["List of key responsibilities and achievements"]
                }
            ],
            "education": [
                {
                    "institution": "School/University name",
                    "degree": "Degree type and field",
                    "graduation_date": "Graduation date",
                    "gpa": "GPA if mentioned",
                    "location": "City, State"
                }
            ],
            "skills": {
                "technical": ["List of technical skills"],
                "soft": ["List of soft skills"],
                "languages": ["Programming languages"],
                "tools": ["Tools and software"]
            },
            "projects": [
                {
                    "name": "Project name",
                    "description": "Project description",
                    "technologies": ["Technologies used"],
                    "url": "Project URL if available"
                }
            ],
            "certifications": [
                {
                    "name": "Certification name",
                    "issuer": "Issuing organization",
                    "date": "Issue date",
                    "expiry": "Expiry date if applicable"
                }
            ],
            "achievements": ["List of notable achievements or awards"]
        }

        Instructions:
        1. Extract only information that is explicitly mentioned in the resume
        2. If information is not available, use null or empty array
        3. Be accurate and don't make assumptions
        4. Return valid JSON format
        5. For dates, keep the original format from the resume

        Resume text:
        """

    async def extract_resume_info(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured information from resume text using Gemini."""
        try:
            prompt = self.create_extraction_prompt() + resume_text
            
            response = await self.model.generate_content_async(prompt)
            
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Parse JSON response
            extracted_data = json.loads(response_text.strip())
            
            logger.info("Successfully extracted resume information")
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {"error": "Failed to parse extracted information"}
        except Exception as e:
            logger.error(f"Error extracting resume info: {e}")
            return {"error": f"Extraction failed: {str(e)}"}

    async def chat_about_resume(self, user_question: str, resume_data: Dict[str, Any]) -> str:
        """Chat about the resume using Gemini AI."""
        try:
            # Create context from resume data
            resume_context = json.dumps(resume_data, indent=2)

            chat_prompt = f"""
            You are a helpful AI assistant specializing in resume analysis and career advice.
            You have access to the following resume data:

            {resume_context}

            The user is asking: "{user_question}"

            Please provide a helpful, informative response based on the resume data. You can:
            - Answer questions about specific details in the resume
            - Provide career advice and suggestions
            - Suggest improvements to the resume
            - Compare skills and experience
            - Explain career progression opportunities
            - Give interview preparation tips based on the background

            Keep your response conversational, helpful, and under 1000 characters for Telegram.
            """

            response = await self.model.generate_content_async(chat_prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error in chat about resume: {e}")
            return "I'm sorry, I encountered an error while processing your question. Please try again."

    async def interview_preparation(self, resume_data: Dict[str, Any], interview_type: str = "general") -> Dict[str, Any]:
        """Generate comprehensive interview preparation based on resume data."""
        try:
            resume_context = json.dumps(resume_data, indent=2)

            interview_prompt = f"""
            You are an expert interview coach and career advisor. Based on the following resume data,
            create a comprehensive interview preparation guide for a {interview_type} interview.

            Resume Data:
            {resume_context}

            Generate a detailed interview preparation response in JSON format with the following structure:

            {{
                "likely_questions": [
                    {{
                        "question": "Sample interview question",
                        "category": "behavioral/technical/situational",
                        "suggested_answer": "How to approach this question based on resume",
                        "key_points": ["Point 1", "Point 2", "Point 3"]
                    }}
                ],
                "strengths_to_highlight": [
                    {{
                        "strength": "Key strength from resume",
                        "evidence": "Specific examples from resume",
                        "how_to_present": "How to articulate this strength"
                    }}
                ],
                "potential_weaknesses": [
                    {{
                        "weakness": "Potential concern",
                        "mitigation": "How to address this concern",
                        "reframe": "How to turn it into a positive"
                    }}
                ],
                "technical_preparation": [
                    {{
                        "skill": "Technical skill from resume",
                        "depth_questions": ["Possible deep-dive questions"],
                        "preparation_tips": "How to prepare for questions about this skill"
                    }}
                ],
                "behavioral_scenarios": [
                    {{
                        "scenario": "STAR method scenario from experience",
                        "situation": "Context from resume",
                        "task": "What needed to be done",
                        "action": "What they did",
                        "result": "Outcome achieved"
                    }}
                ],
                "questions_to_ask": [
                    "Thoughtful questions candidate should ask interviewer"
                ],
                "salary_negotiation": {{
                    "market_range": "Estimated salary range based on experience",
                    "negotiation_points": ["Factors that justify higher compensation"],
                    "preparation_tips": "How to approach salary discussion"
                }},
                "interview_tips": [
                    "Specific tips based on candidate's background"
                ]
            }}

            Make sure all suggestions are directly based on the resume data provided.
            """

            response = await self.model.generate_content_async(interview_prompt)

            # Clean and parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            interview_data = json.loads(response_text.strip())
            logger.info("Successfully generated interview preparation")
            return interview_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse interview preparation JSON: {e}")
            return {"error": "Failed to generate interview preparation"}
        except Exception as e:
            logger.error(f"Error generating interview preparation: {e}")
            return {"error": f"Interview preparation failed: {str(e)}"}

    def format_interview_preparation(self, interview_data: Dict[str, Any]) -> str:
        """Format interview preparation data into readable text."""
        if "error" in interview_data:
            return f"❌ Error: {interview_data['error']}"

        formatted = "🎯 **INTERVIEW PREPARATION GUIDE**\n\n"

        # Likely Questions
        if interview_data.get("likely_questions"):
            formatted += "❓ **Likely Interview Questions:**\n"
            for i, q in enumerate(interview_data["likely_questions"][:5], 1):
                formatted += f"{i}. **{q.get('question', 'N/A')}**\n"
                formatted += f"   Category: {q.get('category', 'N/A')}\n"
                if q.get('key_points'):
                    formatted += f"   Key points: {', '.join(q['key_points'][:3])}\n"
                formatted += "\n"

        # Strengths to Highlight
        if interview_data.get("strengths_to_highlight"):
            formatted += "💪 **Your Key Strengths:**\n"
            for strength in interview_data["strengths_to_highlight"][:3]:
                formatted += f"• **{strength.get('strength', 'N/A')}**\n"
                formatted += f"  Evidence: {strength.get('evidence', 'N/A')}\n\n"

        # Technical Preparation
        if interview_data.get("technical_preparation"):
            formatted += "🔧 **Technical Preparation:**\n"
            for tech in interview_data["technical_preparation"][:3]:
                formatted += f"• **{tech.get('skill', 'N/A')}**\n"
                if tech.get('depth_questions'):
                    formatted += f"  Expect: {tech['depth_questions'][0] if tech['depth_questions'] else 'N/A'}\n"
                formatted += "\n"

        # Questions to Ask
        if interview_data.get("questions_to_ask"):
            formatted += "🤔 **Questions You Should Ask:**\n"
            for i, question in enumerate(interview_data["questions_to_ask"][:3], 1):
                formatted += f"{i}. {question}\n"
            formatted += "\n"

        return formatted[:4000]  # Telegram message limit

    def format_extracted_info(self, data: Dict[str, Any]) -> str:
        """Format extracted information into a readable string."""
        if "error" in data:
            return f"❌ Error: {data['error']}"

        formatted = "📄 **RESUME ANALYSIS**\n\n"

        # Personal Information
        if data.get("personal_info"):
            personal = data["personal_info"]
            formatted += "👤 **Personal Information:**\n"
            if personal.get("name"):
                formatted += f"• Name: {personal['name']}\n"
            if personal.get("email"):
                formatted += f"• Email: {personal['email']}\n"
            if personal.get("phone"):
                formatted += f"• Phone: {personal['phone']}\n"
            if personal.get("location"):
                formatted += f"• Location: {personal['location']}\n"
            if personal.get("linkedin"):
                formatted += f"• LinkedIn: {personal['linkedin']}\n"
            if personal.get("github"):
                formatted += f"• GitHub: {personal['github']}\n"
            formatted += "\n"

        # Summary
        if data.get("summary"):
            formatted += f"📝 **Summary:**\n{data['summary']}\n\n"

        # Experience
        if data.get("experience") and len(data["experience"]) > 0:
            formatted += "💼 **Work Experience:**\n"
            for exp in data["experience"]:
                formatted += f"• **{exp.get('position', 'N/A')}** at {exp.get('company', 'N/A')}\n"
                if exp.get("duration"):
                    formatted += f"  Duration: {exp['duration']}\n"
                if exp.get("location"):
                    formatted += f"  Location: {exp['location']}\n"
                if exp.get("responsibilities"):
                    formatted += "  Key responsibilities:\n"
                    for resp in exp["responsibilities"][:3]:  # Limit to 3 items
                        formatted += f"    - {resp}\n"
                formatted += "\n"

        # Education
        if data.get("education") and len(data["education"]) > 0:
            formatted += "🎓 **Education:**\n"
            for edu in data["education"]:
                formatted += f"• {edu.get('degree', 'N/A')} from {edu.get('institution', 'N/A')}\n"
                if edu.get("graduation_date"):
                    formatted += f"  Graduated: {edu['graduation_date']}\n"
                if edu.get("gpa"):
                    formatted += f"  GPA: {edu['gpa']}\n"
            formatted += "\n"

        # Skills
        if data.get("skills"):
            skills = data["skills"]
            formatted += "🛠️ **Skills:**\n"
            if skills.get("technical"):
                formatted += f"• Technical: {', '.join(skills['technical'][:10])}\n"
            if skills.get("languages"):
                formatted += f"• Programming: {', '.join(skills['languages'][:8])}\n"
            if skills.get("tools"):
                formatted += f"• Tools: {', '.join(skills['tools'][:8])}\n"
            formatted += "\n"

        return formatted[:4000]  # Telegram message limit
