import json
from datetime import datetime
from templates import get_template_html, get_template_styles
import streamlit as st

class ResumeGenerator:
    """Handle resume generation in different formats"""
    
    def __init__(self):
        self.supported_templates = [
            'modern', 'classic', 'creative', 'minimal', 
            'professional', 'executive'
        ]
    
    def generate_html_resume(self, resume_data: dict, template: str = 'modern') -> str:
        """Generate HTML resume with selected template"""
        try:
            # Get template HTML and CSS
            template_html = get_template_html(template)
            template_styles = get_template_styles(template)
            
            # Format the resume data for template
            formatted_data = self._format_resume_data(resume_data)
            
            # Replace placeholders in template
            html_content = self._replace_template_placeholders(
                template_html, formatted_data
            )
            
            # Combine with styles
            full_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{formatted_data.get('full_name', 'Resume')}</title>
                <style>
                    {template_styles}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            return full_html
            
        except Exception as e:
            st.error(f"HTML generation failed: {str(e)}")
            return self._generate_fallback_html(resume_data)
    
    def _format_resume_data(self, resume_data: dict) -> dict:
        """Format resume data for template consumption"""
        formatted = resume_data.copy()
        
        # Format experience
        if 'experience' in formatted:
            for exp in formatted['experience']:
                # Format dates
                start_date = exp.get('start_date', '')
                end_date = exp.get('end_date', 'Present') if not exp.get('is_current') else 'Present'
                exp['date_range'] = f"{start_date} - {end_date}"
                
                # Format description as list
                if isinstance(exp.get('description'), str):
                    exp['description_list'] = [
                        desc.strip() for desc in exp['description'].split('\n') 
                        if desc.strip()
                    ]
        
        # Format education
        if 'education' in formatted:
            for edu in formatted['education']:
                edu['graduation_year'] = edu.get('graduation_date', '')[:4] if edu.get('graduation_date') else ''
        
        # Format skills as comma-separated string
        if 'skills' in formatted and isinstance(formatted['skills'], list):
            formatted['skills_text'] = ', '.join(formatted['skills'])
        
        return formatted
    
    def _replace_template_placeholders(self, template_html: str, data: dict) -> str:
        """Replace placeholders in template with actual data"""
        html = template_html
        
        # Basic information
        html = html.replace('{{full_name}}', data.get('full_name', ''))
        html = html.replace('{{email}}', data.get('email', ''))
        html = html.replace('{{phone}}', data.get('phone', ''))
        html = html.replace('{{location}}', data.get('location', ''))
        html = html.replace('{{linkedin}}', data.get('linkedin', ''))
        html = html.replace('{{website}}', data.get('website', ''))
        html = html.replace('{{summary}}', data.get('summary', ''))
        html = html.replace('{{skills_text}}', data.get('skills_text', ''))
        
        # Experience section
        experience_html = ""
        for exp in data.get('experience', []):
            experience_html += f"""
            <div class="experience-item">
                <div class="job-header">
                    <h3>{exp.get('job_title', '')}</h3>
                    <span class="company">{exp.get('company', '')}</span>
                    <span class="date-range">{exp.get('date_range', '')}</span>
                </div>
                <div class="job-location">{exp.get('location', '')}</div>
                <ul class="job-description">
            """
            for desc in exp.get('description_list', []):
                experience_html += f"<li>{desc}</li>"
            experience_html += "</ul></div>"
        
        html = html.replace('{{experience_section}}', experience_html)
        
        # Education section
        education_html = ""
        for edu in data.get('education', []):
            education_html += f"""
            <div class="education-item">
                <h3>{edu.get('degree', '')}</h3>
                <div class="institution">{edu.get('institution', '')}</div>
                <div class="education-details">
                    <span>{edu.get('field_of_study', '')}</span>
                    <span>{edu.get('graduation_year', '')}</span>
                    {f"<span>GPA: {edu.get('gpa', '')}</span>" if edu.get('gpa') else ''}
                </div>
            </div>
            """
        
        html = html.replace('{{education_section}}', education_html)
        
        # Skills section
        skills_html = ""
        for skill in data.get('skills', []):
            skills_html += f"<span class='skill-tag'>{skill}</span>"
        
        html = html.replace('{{skills_section}}', skills_html)
        
        return html
    
    def _generate_fallback_html(self, resume_data: dict) -> str:
        """Generate basic HTML if template fails"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resume</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin-bottom: 25px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; border-bottom: 1px solid #ccc; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{resume_data.get('full_name', 'Resume')}</h1>
                <p>{resume_data.get('email', '')} | {resume_data.get('phone', '')} | {resume_data.get('location', '')}</p>
            </div>
            
            <div class="section">
                <h2>Professional Summary</h2>
                <p>{resume_data.get('summary', '')}</p>
            </div>
            
            <div class="section">
                <h2>Skills</h2>
                <p>{', '.join(resume_data.get('skills', []))}</p>
            </div>
        </body>
        </html>
        """
    
    def validate_resume_data(self, resume_data: dict) -> dict:
        """Validate resume data and return validation results"""
        errors = []
        warnings = []
        
        # Required fields check
        required_fields = ['full_name', 'email']
        for field in required_fields:
            if not resume_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Email validation
        email = resume_data.get('email', '')
        if email and '@' not in email:
            errors.append("Invalid email format")
        
        # Experience validation
        experience = resume_data.get('experience', [])
        if not experience:
            warnings.append("No work experience added")
        
        for i, exp in enumerate(experience):
            if not exp.get('job_title'):
                errors.append(f"Experience {i+1}: Missing job title")
            if not exp.get('company'):
                errors.append(f"Experience {i+1}: Missing company name")
        
        # Skills validation
        skills = resume_data.get('skills', [])
        if len(skills) < 3:
            warnings.append("Consider adding more skills (recommended: 5-10)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'completeness_score': self._calculate_completeness_score(resume_data)
        }
    
    def _calculate_completeness_score(self, resume_data: dict) -> int:
        """Calculate resume completeness score out of 100"""
        score = 0
        
        # Basic info (30 points)
        if resume_data.get('full_name'): score += 5
        if resume_data.get('email'): score += 5
        if resume_data.get('phone'): score += 5
        if resume_data.get('location'): score += 5
        if resume_data.get('summary'): score += 10
        
        # Experience (40 points)
        experience = resume_data.get('experience', [])
        if experience:
            score += min(40, len(experience) * 10)
        
        # Education (15 points)
        education = resume_data.get('education', [])
        if education:
            score += min(15, len(education) * 7)
        
        # Skills (15 points)
        skills = resume_data.get('skills', [])
        if skills:
            score += min(15, len(skills) * 2)
        
        return min(100, score)
    
    def get_resume_statistics(self, resume_data: dict) -> dict:
        """Get statistics about the resume"""
        return {
            'total_experience_years': self._calculate_experience_years(resume_data),
            'total_jobs': len(resume_data.get('experience', [])),
            'total_skills': len(resume_data.get('skills', [])),
            'education_count': len(resume_data.get('education', [])),
            'word_count': self._count_words(resume_data),
            'completeness_score': self._calculate_completeness_score(resume_data)
        }
    
    def _calculate_experience_years(self, resume_data: dict) -> float:
        """Calculate total years of experience"""
        total_months = 0
        
        for exp in resume_data.get('experience', []):
            start_date = exp.get('start_date')
            end_date = exp.get('end_date')
            
            if start_date:
                try:
                    start = datetime.fromisoformat(start_date)
                    if end_date:
                        end = datetime.fromisoformat(end_date)
                    else:
                        end = datetime.now()
                    
                    months = (end.year - start.year) * 12 + (end.month - start.month)
                    total_months += max(0, months)
                except:
                    continue
        
        return round(total_months / 12, 1)
    
    def _count_words(self, resume_data: dict) -> int:
        """Count total words in resume"""
        word_count = 0
        
        # Count words in text fields
        text_fields = ['summary']
        for field in text_fields:
            if resume_data.get(field):
                word_count += len(resume_data[field].split())
        
        # Count words in experience descriptions
        for exp in resume_data.get('experience', []):
            if exp.get('description'):
                word_count += len(exp['description'].split())
        
        return word_count
