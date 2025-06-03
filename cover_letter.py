import json
import os
from openai import OpenAI
import streamlit as st
from datetime import datetime
from database import get_db_connection
from local_ai_backup import LocalAIBackup

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Initialize local AI backup
local_ai = LocalAIBackup()

def generate_cover_letter(resume_data: dict, company_name: str, position_title: str, 
                         job_description: str = "", tone: str = "Professional", 
                         length: str = "Medium", focus_areas: list = None) -> str:
    """Generate AI-powered cover letter based on resume and job details"""
    
    if focus_areas is None:
        focus_areas = []
    
    try:
        # Extract key information from resume
        experience_summary = _extract_experience_summary(resume_data)
        key_skills = resume_data.get('skills', [])[:8]  # Top 8 skills
        
        # Determine word count based on length preference
        word_counts = {
            "Short": "200-250 words",
            "Medium": "300-400 words", 
            "Long": "450-550 words"
        }
        
        target_length = word_counts.get(length, "300-400 words")
        
        prompt = f"""
        Write a compelling cover letter for {resume_data.get('full_name', 'the candidate')} 
        applying for the {position_title} position at {company_name}.
        
        CANDIDATE INFORMATION:
        - Professional Summary: {resume_data.get('summary', '')}
        - Key Skills: {', '.join(key_skills)}
        - Experience Summary: {experience_summary}
        - Education: {_extract_education_summary(resume_data)}
        
        JOB DETAILS:
        - Position: {position_title}
        - Company: {company_name}
        - Job Description: {job_description}
        
        REQUIREMENTS:
        - Tone: {tone}
        - Length: {target_length}
        - Focus Areas: {', '.join(focus_areas) if focus_areas else 'General fit and qualifications'}
        
        GUIDELINES:
        1. Start with a strong opening that mentions the specific position and company
        2. Highlight relevant experience and achievements that match the job requirements
        3. Demonstrate knowledge of the company/industry when possible
        4. Show enthusiasm and cultural fit
        5. Include specific examples of accomplishments with quantifiable results
        6. End with a confident call to action
        7. Maintain the specified tone throughout
        8. Focus on the specified areas: {', '.join(focus_areas) if focus_areas else 'overall qualifications'}
        
        Format as a professional business letter without address headers.
        Start directly with "Dear Hiring Manager," or "Dear [Department] Team,"
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional career coach and expert cover letter writer. "
                              f"Write in a {tone.lower()} tone and create compelling, personalized cover letters."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        cover_letter = response.choices[0].message.content.strip()
        
        # Save to database
        _save_cover_letter(resume_data, company_name, position_title, cover_letter)
        
        return cover_letter
        
    except Exception as e:
        st.error(f"Cover letter generation failed: {str(e)}")
        return _generate_fallback_cover_letter(resume_data, company_name, position_title)

def _extract_experience_summary(resume_data: dict) -> str:
    """Extract a concise summary of work experience"""
    experience = resume_data.get('experience', [])
    if not experience:
        return "No work experience provided"
    
    # Get most recent 3 experiences
    recent_exp = experience[:3]
    summary_parts = []
    
    for exp in recent_exp:
        job_title = exp.get('job_title', '')
        company = exp.get('company', '')
        if job_title and company:
            summary_parts.append(f"{job_title} at {company}")
    
    return "; ".join(summary_parts)

def _extract_education_summary(resume_data: dict) -> str:
    """Extract education summary"""
    education = resume_data.get('education', [])
    if not education:
        return "No education information provided"
    
    edu = education[0]  # Most recent/relevant education
    degree = edu.get('degree', '')
    field = edu.get('field_of_study', '')
    institution = edu.get('institution', '')
    
    return f"{degree} in {field} from {institution}".strip()

def _save_cover_letter(resume_data: dict, company_name: str, position_title: str, content: str):
    """Save cover letter to database"""
    try:
        conn = get_db_connection()
        if not conn:
            return
            
        cursor = conn.cursor()
        
        # Get user_id from session state or derive from resume_data
        user_id = st.session_state.get('user_id')
        if not user_id:
            return
        
        cursor.execute("""
            INSERT INTO cover_letters (user_id, resume_id, company_name, position_title, content, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, None, company_name, position_title, content, datetime.now()))
        
        conn.commit()
        
    except Exception as e:
        st.error(f"Failed to save cover letter: {str(e)}")
    finally:
        if conn:
            conn.close()

def _generate_fallback_cover_letter(resume_data: dict, company_name: str, position_title: str) -> str:
    """Generate a basic cover letter when AI fails"""
    name = resume_data.get('full_name', 'Candidate')
    
    return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {position_title} position at {company_name}. With my background in {resume_data.get('summary', 'professional experience')}, I am confident that I would be a valuable addition to your team.

My experience includes:
{_format_experience_for_fallback(resume_data.get('experience', []))}

Key skills that I bring to this role include: {', '.join(resume_data.get('skills', [])[:6])}.

I am excited about the opportunity to contribute to {company_name} and would welcome the chance to discuss how my background and enthusiasm can benefit your organization.

Thank you for your consideration. I look forward to hearing from you.

Sincerely,
{name}"""

def _format_experience_for_fallback(experience_list: list) -> str:
    """Format experience for fallback cover letter"""
    if not experience_list:
        return "• Relevant professional experience in the field"
    
    formatted = []
    for exp in experience_list[:3]:
        title = exp.get('job_title', 'Professional')
        company = exp.get('company', 'Previous Organization')
        formatted.append(f"• {title} at {company}")
    
    return '\n'.join(formatted)

def get_cover_letter_templates() -> dict:
    """Return available cover letter templates"""
    return {
        'standard': {
            'name': 'Standard Business',
            'description': 'Traditional professional format',
            'best_for': 'Corporate positions, formal industries'
        },
        'modern': {
            'name': 'Modern Professional',
            'description': 'Contemporary style with personality',
            'best_for': 'Tech, startups, creative roles'
        },
        'executive': {
            'name': 'Executive Level',
            'description': 'Senior-level positioning',
            'best_for': 'C-level, VP, Director positions'
        },
        'creative': {
            'name': 'Creative Industry',
            'description': 'Shows creativity and innovation',
            'best_for': 'Design, marketing, media roles'
        },
        'academic': {
            'name': 'Academic/Research',
            'description': 'Scholarly and research-focused',
            'best_for': 'University, research, education roles'
        }
    }

def customize_cover_letter_tone(base_letter: str, new_tone: str) -> str:
    """Adjust the tone of an existing cover letter"""
    try:
        prompt = f"""
        Rewrite this cover letter to match a {new_tone} tone while keeping all the factual content the same.
        
        Original Cover Letter:
        {base_letter}
        
        New Tone: {new_tone}
        
        Tone Guidelines:
        - Professional: Formal, business-appropriate language
        - Enthusiastic: Show excitement and energy
        - Conservative: Traditional, formal approach
        - Creative: Show personality and innovation
        
        Keep the same structure and key points, only adjust the language and style.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at adapting writing tone while preserving content."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        st.error(f"Tone adjustment failed: {str(e)}")
        return base_letter

def generate_cover_letter_variations(resume_data: dict, company_name: str, 
                                   position_title: str, job_description: str) -> dict:
    """Generate multiple cover letter variations for comparison"""
    variations = {}
    
    tones = ['Professional', 'Enthusiastic', 'Conservative']
    lengths = ['Short', 'Medium']
    
    for tone in tones:
        for length in lengths:
            try:
                variation_key = f"{tone}_{length}"
                cover_letter = generate_cover_letter(
                    resume_data=resume_data,
                    company_name=company_name,
                    position_title=position_title,
                    job_description=job_description,
                    tone=tone,
                    length=length
                )
                variations[variation_key] = {
                    'content': cover_letter,
                    'tone': tone,
                    'length': length,
                    'word_count': len(cover_letter.split())
                }
            except Exception as e:
                continue
    
    return variations

def analyze_cover_letter_effectiveness(cover_letter: str, job_description: str = "") -> dict:
    """Analyze cover letter effectiveness and provide feedback"""
    try:
        prompt = f"""
        Analyze this cover letter for effectiveness and provide constructive feedback.
        
        Cover Letter:
        {cover_letter}
        
        Job Description Context:
        {job_description}
        
        Evaluate and provide feedback in JSON format:
        {{
            "overall_score": <score_out_of_100>,
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "suggestions": ["suggestion1", "suggestion2"],
            "keyword_optimization": <score_out_of_100>,
            "tone_assessment": "professional/enthusiastic/conservative/creative",
            "structure_score": <score_out_of_100>,
            "personalization_score": <score_out_of_100>,
            "call_to_action_score": <score_out_of_100>
        }}
        
        Focus on:
        - Relevance to job requirements
        - Professional tone and language
        - Structure and flow
        - Personalization and specificity
        - Call to action effectiveness
        - Keyword optimization for ATS
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional career coach and hiring manager with expertise in evaluating cover letters."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=600
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        st.error(f"Cover letter analysis failed: {str(e)}")
        return {
            "overall_score": 75,
            "strengths": ["Clear communication"],
            "weaknesses": ["Could be more specific"],
            "suggestions": ["Add more quantifiable achievements"],
            "keyword_optimization": 70,
            "tone_assessment": "professional",
            "structure_score": 80,
            "personalization_score": 70,
            "call_to_action_score": 75
        }

def get_user_cover_letters(user_id: int) -> list:
    """Get all cover letters for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, company_name, position_title, content, created_at
            FROM cover_letters 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """, (user_id,))
        
        results = cursor.fetchall()
        cover_letters = []
        
        for result in results:
            cover_letters.append({
                'id': result[0],
                'company_name': result[1],
                'position_title': result[2],
                'content': result[3],
                'created_at': result[4].isoformat() if result[4] else '',
                'word_count': len(result[3].split()) if result[3] else 0
            })
        
        return cover_letters
        
    except Exception as e:
        st.error(f"Error loading cover letters: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def delete_cover_letter(cover_letter_id: int, user_id: int) -> bool:
    """Delete a cover letter"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM cover_letters WHERE id = %s AND user_id = %s",
            (cover_letter_id, user_id)
        )
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        st.error(f"Error deleting cover letter: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def suggest_cover_letter_improvements(cover_letter: str, target_role: str = "") -> list:
    """Suggest specific improvements for cover letter"""
    try:
        prompt = f"""
        Review this cover letter and suggest 5-7 specific improvements.
        Target Role: {target_role}
        
        Cover Letter:
        {cover_letter}
        
        Provide specific, actionable suggestions in JSON format:
        {{
            "improvements": [
                "specific improvement 1",
                "specific improvement 2",
                "specific improvement 3"
            ]
        }}
        
        Focus on:
        - Making achievements more quantifiable
        - Improving keyword usage for ATS
        - Enhancing company/role-specific customization
        - Strengthening the opening and closing
        - Better showcasing relevant skills
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional cover letter coach providing specific improvement suggestions."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=400
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('improvements', [])
        
    except Exception as e:
        return [
            "Add specific quantifiable achievements from your experience",
            "Research the company more and mention specific reasons for interest",
            "Include more keywords from the job description",
            "Strengthen your opening sentence to be more engaging",
            "Make your call to action more confident and specific"
        ]

def export_cover_letter(cover_letter: str, filename: str = "cover_letter") -> bytes:
    """Export cover letter to various formats"""
    try:
        from docx import Document
        from docx.shared import Inches
        import io
        
        # Create Word document
        doc = Document()
        
        # Set margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
        
        # Add cover letter content
        paragraphs = cover_letter.split('\n\n')
        for para in paragraphs:
            if para.strip():
                doc.add_paragraph(para.strip())
        
        # Save to bytes
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"Cover letter export failed: {str(e)}")
        return b""

