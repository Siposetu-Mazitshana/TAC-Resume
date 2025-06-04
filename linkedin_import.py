import json
import re
import requests
from datetime import datetime
import streamlit as st
from typing import Dict, List, Optional
import os
from openai import OpenAI
from local_ai_backup import LocalAIBackup

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Initialize local AI backup
local_ai = LocalAIBackup()

def import_linkedin_profile(linkedin_url: str) -> Optional[Dict]:
    """Import LinkedIn profile data and convert to resume format"""
    try:
        # Validate LinkedIn URL
        if not _validate_linkedin_url(linkedin_url):
            st.error("Please provide a valid LinkedIn profile URL")
            return None
        
        # For demo purposes, we'll use AI to parse publicly available information
        # In a production environment, you would use LinkedIn's official API
        
        # Extract profile data using web scraping (simplified)
        profile_data = _extract_profile_data(linkedin_url)
        
        if not profile_data:
            return None
        
        # Convert to resume format
        resume_data = _convert_linkedin_to_resume(profile_data)
        
        return resume_data
        
    except Exception as e:
        st.error(f"LinkedIn import failed: {str(e)}")
        return None

def _validate_linkedin_url(url: str) -> bool:
    """Validate LinkedIn profile URL format"""
    linkedin_pattern = r'^https?://(www\.)?linkedin\.com/in/[\w\-]+/?$'
    return bool(re.match(linkedin_pattern, url))

def _extract_profile_data(linkedin_url: str) -> Optional[Dict]:
    """Extract profile data from LinkedIn URL"""
    try:
        # Note: This is a simplified implementation
        # In production, you would use LinkedIn's official API or approved scraping methods
        
        # For now, we'll simulate profile extraction and use AI to help structure the data
        # This would require the user to manually input their LinkedIn profile info
        
        st.info("🔗 LinkedIn Integration Notice: Please manually enter your LinkedIn profile information below for import.")
        
        # Create a form for manual LinkedIn data entry
        with st.form("linkedin_manual_entry"):
            st.subheader("LinkedIn Profile Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name")
                headline = st.text_input("Professional Headline")
                location = st.text_input("Location")
                industry = st.text_input("Industry")
            
            with col2:
                company = st.text_input("Current Company")
                position = st.text_input("Current Position")
                email = st.text_input("Email Address")
                phone = st.text_input("Phone Number")
            
            summary = st.text_area("Professional Summary/About Section", height=150)
            
            # Experience section
            st.subheader("Experience")
            experience_text = st.text_area("Paste your experience details (job titles, companies, descriptions)", height=200)
            
            # Education section
            st.subheader("Education")
            education_text = st.text_area("Paste your education details (degrees, schools, dates)", height=100)
            
            # Skills section
            st.subheader("Skills")
            skills_text = st.text_input("Enter skills (comma-separated)")
            
            submitted = st.form_submit_button("Import from LinkedIn")
            
            if submitted and name:
                # Process the manually entered data
                profile_data = {
                    'name': name,
                    'headline': headline,
                    'location': location,
                    'industry': industry,
                    'current_company': company,
                    'current_position': position,
                    'email': email,
                    'phone': phone,
                    'summary': summary,
                    'experience_text': experience_text,
                    'education_text': education_text,
                    'skills_text': skills_text,
                    'linkedin_url': linkedin_url
                }
                
                return profile_data
        
        return None
        
    except Exception as e:
        st.error(f"Profile extraction failed: {str(e)}")
        return None

def _convert_linkedin_to_resume(profile_data: Dict) -> Dict:
    """Convert LinkedIn profile data to resume format"""
    try:
        # Use AI to help parse and structure the LinkedIn data
        parsed_data = _parse_linkedin_with_ai(profile_data)
        
        # Build resume structure
        resume_data = {
            'full_name': profile_data.get('name', ''),
            'email': profile_data.get('email', ''),
            'phone': profile_data.get('phone', ''),
            'location': profile_data.get('location', ''),
            'linkedin': profile_data.get('linkedin_url', ''),
            'website': '',
            'summary': profile_data.get('summary', ''),
            'experience': parsed_data.get('experience', []),
            'education': parsed_data.get('education', []),
            'skills': parsed_data.get('skills', [])
        }
        
        # Clean and validate the data
        resume_data = _clean_resume_data(resume_data)
        
        return resume_data
        
    except Exception as e:
        st.error(f"Conversion to resume format failed: {str(e)}")
        return {}

def _parse_linkedin_with_ai(profile_data: Dict) -> Dict:
    """Use AI to parse LinkedIn text data into structured format"""
    try:
        # Parse experience
        experience_data = []
        if profile_data.get('experience_text'):
            experience_data = _parse_experience_with_ai(profile_data['experience_text'])
        
        # Add current position if provided separately
        if profile_data.get('current_company') and profile_data.get('current_position'):
            current_exp = {
                'job_title': profile_data['current_position'],
                'company': profile_data['current_company'],
                'location': profile_data.get('location', ''),
                'start_date': datetime.now().strftime('%Y-%m'),
                'end_date': None,
                'is_current': True,
                'description': f"Current position at {profile_data['current_company']}"
            }
            experience_data.insert(0, current_exp)
        
        # Parse education
        education_data = []
        if profile_data.get('education_text'):
            education_data = _parse_education_with_ai(profile_data['education_text'])
        
        # Parse skills
        skills_data = []
        if profile_data.get('skills_text'):
            skills_list = [skill.strip() for skill in profile_data['skills_text'].split(',')]
            skills_data = [skill for skill in skills_list if skill]
        
        return {
            'experience': experience_data,
            'education': education_data,
            'skills': skills_data
        }
        
    except Exception as e:
        st.error(f"AI parsing failed: {str(e)}")
        return {'experience': [], 'education': [], 'skills': []}

def _parse_experience_with_ai(experience_text: str) -> List[Dict]:
    """Parse experience text using AI"""
    try:
        prompt = f"""
        Parse this LinkedIn experience text into structured JSON format.
        
        Experience Text:
        {experience_text}
        
        Convert to JSON array with this format:
        {{
            "experience": [
                {{
                    "job_title": "Job Title",
                    "company": "Company Name",
                    "location": "City, State/Country",
                    "start_date": "YYYY-MM",
                    "end_date": "YYYY-MM or null if current",
                    "is_current": false,
                    "description": "Job description and achievements"
                }}
            ]
        }}
        
        Extract all positions mentioned. If dates are unclear, use reasonable estimates.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at parsing LinkedIn profiles and extracting structured career information."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=800
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('experience', [])
        
    except Exception as e:
        st.error(f"Experience parsing failed: {str(e)}")
        return []

def _parse_education_with_ai(education_text: str) -> List[Dict]:
    """Parse education text using AI"""
    try:
        prompt = f"""
        Parse this LinkedIn education text into structured JSON format.
        
        Education Text:
        {education_text}
        
        Convert to JSON array with this format:
        {{
            "education": [
                {{
                    "degree": "Degree Name",
                    "institution": "School/University Name",
                    "field_of_study": "Field of Study",
                    "graduation_date": "YYYY-MM-DD",
                    "gpa": "GPA if mentioned",
                    "location": "City, State/Country"
                }}
            ]
        }}
        
        Extract all educational institutions mentioned.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at parsing educational information from LinkedIn profiles."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=600
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('education', [])
        
    except Exception as e:
        st.error(f"Education parsing failed: {str(e)}")
        return []

def _clean_resume_data(resume_data: Dict) -> Dict:
    """Clean and validate resume data"""
    cleaned_data = resume_data.copy()
    
    # Clean phone number
    if cleaned_data.get('phone'):
        phone = re.sub(r'[^\d\+\-\(\)\s]', '', cleaned_data['phone'])
        cleaned_data['phone'] = phone
    
    # Clean email
    if cleaned_data.get('email'):
        email = cleaned_data['email'].strip().lower()
        if '@' not in email:
            cleaned_data['email'] = ''
    
    # Ensure skills is a list
    if isinstance(cleaned_data.get('skills'), str):
        cleaned_data['skills'] = [skill.strip() for skill in cleaned_data['skills'].split(',') if skill.strip()]
    
    # Validate experience dates
    for exp in cleaned_data.get('experience', []):
        if exp.get('start_date'):
            try:
                datetime.strptime(exp['start_date'], '%Y-%m')
            except:
                exp['start_date'] = datetime.now().strftime('%Y-%m')
        
        if exp.get('end_date') and not exp.get('is_current'):
            try:
                datetime.strptime(exp['end_date'], '%Y-%m')
            except:
                exp['end_date'] = datetime.now().strftime('%Y-%m')
    
    # Validate education dates
    for edu in cleaned_data.get('education', []):
        if edu.get('graduation_date'):
            try:
                datetime.strptime(edu['graduation_date'], '%Y-%m-%d')
            except:
                try:
                    # Try just year
                    year = int(edu['graduation_date'][:4])
                    edu['graduation_date'] = f"{year}-06-01"
                except:
                    edu['graduation_date'] = datetime.now().strftime('%Y-%m-%d')
    
    return cleaned_data

def enhance_linkedin_import_with_ai(resume_data: Dict, target_industry: str = "") -> Dict:
    """Enhance imported LinkedIn data with AI suggestions"""
    try:
        prompt = f"""
        Enhance this resume data imported from LinkedIn. Improve the content and suggest additions.
        Target Industry: {target_industry}
        
        Current Resume Data:
        {json.dumps(resume_data, indent=2)}
        
        Provide enhanced version in JSON format with:
        1. Improved professional summary
        2. Enhanced job descriptions with action verbs and achievements
        3. Additional relevant skills for the target industry
        4. Better formatting and keyword optimization
        
        Return the enhanced resume data in the same format.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume writer specializing in LinkedIn profile optimization."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1200
        )
        
        enhanced_data = json.loads(response.choices[0].message.content)
        
        # Merge enhanced data with original, preserving structure
        return _merge_enhanced_data(resume_data, enhanced_data)
        
    except Exception as e:
        st.error(f"AI enhancement failed: {str(e)}")
        return resume_data

def _merge_enhanced_data(original: Dict, enhanced: Dict) -> Dict:
    """Merge enhanced AI data with original resume data"""
    merged = original.copy()
    
    # Update text fields if enhanced versions are better
    text_fields = ['summary']
    for field in text_fields:
        if enhanced.get(field) and len(enhanced[field]) > len(original.get(field, '')):
            merged[field] = enhanced[field]
    
    # Merge skills (add new ones, keep existing)
    if enhanced.get('skills'):
        existing_skills = set(skill.lower() for skill in original.get('skills', []))
        for skill in enhanced['skills']:
            if skill.lower() not in existing_skills:
                merged.setdefault('skills', []).append(skill)
    
    # Enhance experience descriptions
    if enhanced.get('experience') and original.get('experience'):
        for i, exp in enumerate(original['experience']):
            if i < len(enhanced['experience']):
                enhanced_exp = enhanced['experience'][i]
                if len(enhanced_exp.get('description', '')) > len(exp.get('description', '')):
                    merged['experience'][i]['description'] = enhanced_exp['description']
    
    return merged

def validate_linkedin_import(resume_data: Dict) -> Dict:
    """Validate imported LinkedIn data"""
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': []
    }
    
    # Check required fields
    required_fields = ['full_name', 'email']
    for field in required_fields:
        if not resume_data.get(field):
            validation_result['errors'].append(f"Missing required field: {field}")
            validation_result['is_valid'] = False
    
    # Check email format
    email = resume_data.get('email', '')
    if email and '@' not in email:
        validation_result['errors'].append("Invalid email format")
        validation_result['is_valid'] = False
    
    # Check experience
    experience = resume_data.get('experience', [])
    if not experience:
        validation_result['warnings'].append("No work experience found")
    else:
        for i, exp in enumerate(experience):
            if not exp.get('job_title'):
                validation_result['warnings'].append(f"Experience {i+1}: Missing job title")
            if not exp.get('company'):
                validation_result['warnings'].append(f"Experience {i+1}: Missing company name")
    
    # Check education
    education = resume_data.get('education', [])
    if not education:
        validation_result['warnings'].append("No education information found")
    
    # Check skills
    skills = resume_data.get('skills', [])
    if len(skills) < 3:
        validation_result['suggestions'].append("Consider adding more skills (recommended: 5-10)")
    
    # Suggestions for improvement
    if not resume_data.get('summary'):
        validation_result['suggestions'].append("Add a professional summary to make your profile more compelling")
    
    if not resume_data.get('phone'):
        validation_result['suggestions'].append("Consider adding a phone number for better contact accessibility")
    
    return validation_result

def export_to_linkedin_format(resume_data: Dict) -> str:
    """Export resume data back to LinkedIn-friendly format"""
    try:
        # Create LinkedIn-style summary
        linkedin_text = f"**{resume_data.get('full_name', '')}**\n"
        linkedin_text += f"{resume_data.get('summary', '')}\n\n"
        
        # Experience section
        if resume_data.get('experience'):
            linkedin_text += "**EXPERIENCE**\n\n"
            for exp in resume_data['experience']:
                linkedin_text += f"**{exp.get('job_title', '')}** at **{exp.get('company', '')}**\n"
                linkedin_text += f"{exp.get('location', '')} | {exp.get('start_date', '')} - {'Present' if exp.get('is_current') else exp.get('end_date', '')}\n"
                linkedin_text += f"{exp.get('description', '')}\n\n"
        
        # Education section
        if resume_data.get('education'):
            linkedin_text += "**EDUCATION**\n\n"
            for edu in resume_data['education']:
                linkedin_text += f"**{edu.get('degree', '')}** in {edu.get('field_of_study', '')}\n"
                linkedin_text += f"{edu.get('institution', '')} | {edu.get('graduation_date', '')}\n\n"
        
        # Skills section
        if resume_data.get('skills'):
            linkedin_text += "**SKILLS**\n"
            linkedin_text += " • ".join(resume_data['skills'])
        
        return linkedin_text
        
    except Exception as e:
        st.error(f"Export to LinkedIn format failed: {str(e)}")
        return ""

def get_linkedin_optimization_suggestions(resume_data: Dict) -> List[str]:
    """Get LinkedIn profile optimization suggestions"""
    suggestions = []
    
    # Headline suggestions
    if not resume_data.get('summary') or len(resume_data.get('summary', '')) < 50:
        suggestions.append("🎯 Create a compelling professional headline that showcases your value proposition")
    
    # Skills optimization
    skills_count = len(resume_data.get('skills', []))
    if skills_count < 5:
        suggestions.append("🔧 Add more relevant skills to your profile (LinkedIn allows up to 50)")
    elif skills_count > 30:
        suggestions.append("✂️ Consider focusing on your most relevant skills (quality over quantity)")
    
    # Experience optimization
    experience = resume_data.get('experience', [])
    if experience:
        for exp in experience:
            if not exp.get('description') or len(exp.get('description', '')) < 100:
                suggestions.append(f"📝 Expand the description for your role at {exp.get('company', 'this company')} with specific achievements")
    
    # Contact information
    if not resume_data.get('phone'):
        suggestions.append("📞 Add contact information to make it easier for recruiters to reach you")
    
    # Professional summary
    summary = resume_data.get('summary', '')
    if summary and 'I am' in summary:
        suggestions.append("💡 Rewrite your summary in third person for a more professional tone")
    
    return suggestions

