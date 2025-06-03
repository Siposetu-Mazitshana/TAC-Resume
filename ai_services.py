import json
import os
from openai import OpenAI
import streamlit as st
from local_ai_backup import LocalAIBackup

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Initialize local AI backup
local_ai = LocalAIBackup()

def generate_professional_summary(name: str, experience: list, skills: list, target_role: str = "") -> str:
    """Generate a professional summary using AI with local backup"""
    # Try OpenAI first if available
    if openai_client:
        try:
            experience_text = ""
            if experience:
                for exp in experience[:3]:  # Use top 3 experiences
                    experience_text += f"- {exp.get('job_title', '')} at {exp.get('company', '')}\n"
            
            skills_text = ", ".join(skills[:10]) if skills else ""
            
            prompt = f"""
            Create a professional resume summary for {name}. 
            
            Experience:
            {experience_text}
            
            Key Skills: {skills_text}
            Target Role: {target_role}
            
            Write a compelling 2-3 sentence professional summary that highlights:
            - Years of experience and expertise
            - Key achievements and value proposition
            - Relevant skills for the target role
            
            Make it ATS-friendly and engaging. Respond with just the summary text.
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.warning("Primary AI service unavailable, using backup system")
    
    # Fallback to local AI
    try:
        return local_ai.generate_professional_summary(name, experience, skills, target_role)
    except Exception as e:
        st.error(f"All AI services failed: {str(e)}")
        return "Experienced professional with a proven track record of delivering results and driving organizational success."

def generate_job_description(job_title: str, basic_description: str) -> str:
    """Enhance job description using AI with local backup"""
    # Try OpenAI first if available
    if openai_client:
        try:
            prompt = f"""
            Enhance this job description for a {job_title} position. Make it more professional, 
            action-oriented, and quantifiable where possible.
            
            Original description:
            {basic_description}
            
            Improve it by:
            - Using strong action verbs
            - Adding industry-specific keywords
            - Making achievements quantifiable when possible
            - Ensuring ATS compatibility
            - Keeping it concise but impactful
            
            Return only the enhanced description as bullet points.
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.warning("Primary AI service unavailable, using backup system")
    
    # Fallback to local AI
    try:
        return local_ai.enhance_job_description(job_title, basic_description)
    except Exception as e:
        st.error(f"All AI services failed: {str(e)}")
        return basic_description

def get_content_suggestions(job_role: str, content_type: str = "skills") -> list:
    """Get AI suggestions for resume content"""
    # Try OpenAI first if available
    if openai_client:
        try:
            if content_type == "skills":
                prompt = f"""
                List 8-10 relevant technical and soft skills for a {job_role} position.
                Focus on current industry standards and in-demand skills.
                Return as a JSON array of strings.
                """
            elif content_type == "keywords":
                prompt = f"""
                List 10-12 important ATS keywords for a {job_role} position.
                Include industry-specific terms and common requirements.
                Return as a JSON array of strings.
                """
            else:
                return []
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a career expert. Provide practical, relevant suggestions."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result.get("suggestions", result.get("skills", result.get("keywords", [])))
            
        except Exception as e:
            st.warning("Primary AI service unavailable, using backup system")
    
    # Fallback to local AI
    try:
        return local_ai.get_content_suggestions(job_role, content_type)
    except Exception as e:
        st.error(f"All AI services failed: {str(e)}")
        return []

def optimize_for_ats(resume_data: dict, job_description: str = "") -> dict:
    """Optimize resume content for ATS systems"""
    # Try OpenAI first if available
    if openai_client:
        try:
            prompt = f"""
            Analyze this resume data and provide ATS optimization suggestions.
            
            Resume Data: {json.dumps(resume_data, indent=2)}
            Job Description: {job_description}
            
            Provide suggestions in JSON format:
            {{
                "ats_score": <score_out_of_100>,
                "improvements": [
                    "suggestion 1",
                    "suggestion 2"
                ],
                "missing_keywords": ["keyword1", "keyword2"],
                "formatting_issues": ["issue1", "issue2"]
            }}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an ATS optimization expert. Provide actionable feedback."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            if content:
                return json.loads(content)
                
        except Exception as e:
            st.warning("Primary AI service unavailable, using backup system")
    
    # Fallback to local AI
    try:
        return local_ai.optimize_for_ats(resume_data, job_description)
    except Exception as e:
        st.error(f"All AI services failed: {str(e)}")
        return {
            "ats_score": 75,
            "improvements": ["Add more industry-specific keywords"],
            "missing_keywords": [],
            "formatting_issues": []
        }

def analyze_job_posting(job_description: str) -> dict:
    """Analyze job posting to extract key requirements"""
    # Try OpenAI first if available
    if openai_client:
        try:
            prompt = f"""
            Analyze this job posting and extract key information in JSON format:
            
            Job Description:
            {job_description}
            
            Extract:
            {{
                "required_skills": ["skill1", "skill2"],
                "preferred_skills": ["skill1", "skill2"],
                "requirements": ["requirement1", "requirement2"],
                "responsibilities": ["responsibility1", "responsibility2"],
                "keywords": ["keyword1", "keyword2"],
                "experience_level": "entry/mid/senior",
                "company_size": "startup/medium/enterprise",
                "industry": "industry_name"
            }}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a job analysis expert. Extract precise, relevant information."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            if content:
                return json.loads(content)
                
        except Exception as e:
            st.warning("Primary AI service unavailable, using backup system")
    
    # Fallback to local AI
    try:
        return local_ai.analyze_job_posting(job_description)
    except Exception as e:
        st.error(f"All AI services failed: {str(e)}")
        return {}

def generate_interview_questions(resume_data: dict, job_description: str = "") -> list:
    """Generate potential interview questions based on resume and job"""
    # Try OpenAI first if available
    if openai_client:
        try:
            prompt = f"""
            Based on this resume and job description, generate 8-10 potential interview questions.
            
            Resume: {json.dumps(resume_data, indent=2)}
            Job Description: {job_description}
            
            Generate questions that:
            - Test technical skills mentioned in resume
            - Explore experience and achievements
            - Assess cultural fit
            - Challenge problem-solving abilities
            
            Return as JSON array of question strings.
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an HR expert creating thoughtful interview questions."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result.get("questions", [])
                
        except Exception as e:
            st.warning("Primary AI service unavailable, using backup system")
    
    # Fallback to basic question generation
    try:
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience', [])
        
        questions = [
            "Tell me about yourself and your background.",
            "What interests you most about this position?",
            "Describe your greatest professional achievement.",
            "How do you handle challenging situations at work?",
            "Where do you see yourself in 5 years?"
        ]
        
        # Add skill-based questions
        if skills:
            questions.extend([
                f"How would you rate your expertise in {skills[0]}?",
                f"Can you give an example of how you've used {skills[1] if len(skills) > 1 else skills[0]} in a project?"
            ])
        
        # Add experience-based questions
        if experience:
            recent_job = experience[0].get('job_title', 'your recent role')
            questions.append(f"What were your main responsibilities as {recent_job}?")
        
        return questions[:8]
        
    except Exception as e:
        st.error(f"All AI services failed: {str(e)}")
        return []

def score_resume_content(resume_data: dict) -> dict:
    """Score resume content quality and completeness"""
    try:
        prompt = f"""
        Score this resume content on a scale of 1-100 and provide detailed feedback.
        
        Resume Data: {json.dumps(resume_data, indent=2)}
        
        Evaluate:
        - Completeness of sections
        - Quality of content
        - Professional language
        - Quantifiable achievements
        - Keyword optimization
        
        Return JSON:
        {{
            "overall_score": <score>,
            "section_scores": {{
                "summary": <score>,
                "experience": <score>,
                "education": <score>,
                "skills": <score>
            }},
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"]
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume reviewer with expertise in career coaching."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=400
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        st.error(f"Resume scoring failed: {str(e)}")
        return {
            "overall_score": 75,
            "section_scores": {"summary": 80, "experience": 75, "education": 70, "skills": 80},
            "strengths": ["Good professional experience"],
            "improvements": ["Add more quantifiable achievements"]
        }
