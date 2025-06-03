import re
import random
from typing import List, Dict
import streamlit as st

class LocalAIBackup:
    """Local AI backup service using rule-based text generation"""
    
    def __init__(self):
        self.action_verbs = [
            "developed", "managed", "led", "implemented", "created", "designed",
            "optimized", "streamlined", "enhanced", "delivered", "coordinated",
            "executed", "supervised", "analyzed", "improved", "established",
            "collaborated", "facilitated", "spearheaded", "achieved", "increased"
        ]
        
        self.business_terms = [
            "efficiency", "productivity", "performance", "quality", "revenue",
            "customer satisfaction", "team collaboration", "strategic initiatives",
            "operational excellence", "innovation", "growth", "profitability",
            "market share", "cost reduction", "process improvement"
        ]
        
        self.skill_categories = {
            "technical": [
                "Python", "JavaScript", "SQL", "React", "Node.js", "AWS",
                "Docker", "Git", "Linux", "MongoDB", "PostgreSQL", "API Development"
            ],
            "business": [
                "Project Management", "Strategic Planning", "Business Analysis",
                "Market Research", "Financial Analysis", "Leadership", "Communication"
            ],
            "creative": [
                "Graphic Design", "UI/UX Design", "Content Creation", "Brand Management",
                "Social Media Marketing", "Video Editing", "Adobe Creative Suite"
            ]
        }

    def generate_professional_summary(self, name: str, experience: list, skills: list, target_role: str = "") -> str:
        """Generate professional summary using rule-based approach"""
        try:
            # Calculate experience years
            total_years = self._calculate_years_from_experience(experience)
            
            # Determine experience level
            if total_years < 2:
                level = "emerging"
            elif total_years < 5:
                level = "experienced"
            elif total_years < 10:
                level = "seasoned"
            else:
                level = "senior"
            
            # Get primary skills
            primary_skills = skills[:3] if skills else ["professional skills"]
            
            # Generate summary templates
            templates = [
                f"{level.capitalize()} professional with {total_years}+ years of experience in {', '.join(primary_skills[:2])}. Proven track record of delivering high-quality results and driving organizational success through innovative solutions and strategic thinking.",
                
                f"Results-driven {level} professional specializing in {', '.join(primary_skills[:2])}. With {total_years}+ years of experience, demonstrates expertise in {random.choice(self.business_terms)} and {random.choice(self.business_terms)}.",
                
                f"Dynamic {level} professional with {total_years}+ years of experience leveraging {', '.join(primary_skills[:2])} to drive business growth. Known for {random.choice(self.business_terms)} and exceptional problem-solving abilities."
            ]
            
            return random.choice(templates)
            
        except Exception as e:
            return f"Experienced professional with expertise in {', '.join(skills[:3]) if skills else 'multiple domains'}. Committed to delivering exceptional results and contributing to organizational success."

    def enhance_job_description(self, job_title: str, basic_description: str) -> str:
        """Enhance job description using rule-based improvement"""
        try:
            if not basic_description:
                return f"• {random.choice(self.action_verbs).capitalize()} key responsibilities related to {job_title.lower()}"
            
            # Split into sentences/bullet points
            sentences = re.split(r'[.•\n]', basic_description)
            enhanced_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # Add action verb if missing
                if not any(verb in sentence.lower() for verb in self.action_verbs):
                    action_verb = random.choice(self.action_verbs)
                    sentence = f"{action_verb.capitalize()} {sentence.lower()}"
                
                # Add quantifiable elements if missing numbers
                if not re.search(r'\d+', sentence):
                    metrics = ["20%", "15+", "$50K", "10-member", "3 projects", "2x improvement"]
                    if random.random() < 0.3:  # 30% chance to add metric
                        sentence += f" resulting in {random.choice(metrics)} improvement"
                
                enhanced_sentences.append(f"• {sentence}")
            
            return '\n'.join(enhanced_sentences[:5])  # Limit to 5 bullet points
            
        except Exception as e:
            return basic_description

    def get_content_suggestions(self, job_role: str, content_type: str = "skills") -> list:
        """Get content suggestions based on job role"""
        try:
            job_role_lower = job_role.lower()
            
            if content_type == "skills":
                suggested_skills = []
                
                # Technical roles
                if any(term in job_role_lower for term in ["developer", "engineer", "programmer", "technical"]):
                    suggested_skills.extend(self.skill_categories["technical"][:6])
                
                # Business roles
                elif any(term in job_role_lower for term in ["manager", "analyst", "coordinator", "business"]):
                    suggested_skills.extend(self.skill_categories["business"][:6])
                
                # Creative roles
                elif any(term in job_role_lower for term in ["designer", "creative", "marketing", "content"]):
                    suggested_skills.extend(self.skill_categories["creative"][:6])
                
                # General skills for any role
                else:
                    suggested_skills.extend([
                        "Communication", "Problem Solving", "Time Management",
                        "Teamwork", "Leadership", "Adaptability"
                    ])
                
                return suggested_skills[:8]
            
            elif content_type == "keywords":
                keywords = []
                
                # Role-specific keywords
                if "manager" in job_role_lower:
                    keywords.extend(["leadership", "team management", "strategic planning", "budget management"])
                elif "analyst" in job_role_lower:
                    keywords.extend(["data analysis", "reporting", "research", "insights"])
                elif "developer" in job_role_lower:
                    keywords.extend(["software development", "coding", "debugging", "testing"])
                
                # General business keywords
                keywords.extend(["collaboration", "innovation", "efficiency", "quality assurance"])
                
                return keywords[:10]
            
            return []
            
        except Exception as e:
            return []

    def optimize_for_ats(self, resume_data: dict, job_description: str = "") -> dict:
        """Basic ATS optimization suggestions"""
        try:
            suggestions = []
            missing_keywords = []
            formatting_issues = []
            
            # Check for action verbs
            resume_text = self._extract_text_from_resume(resume_data)
            action_verb_count = sum(1 for verb in self.action_verbs if verb in resume_text.lower())
            
            if action_verb_count < 3:
                suggestions.append("Add more action verbs to describe your achievements")
            
            # Check for quantifiable achievements
            numbers = re.findall(r'\d+[%$]?', resume_text)
            if len(numbers) < 3:
                suggestions.append("Include more quantifiable achievements with numbers and percentages")
            
            # Check sections completeness
            if not resume_data.get('skills'):
                suggestions.append("Add a skills section with relevant keywords")
            
            if not resume_data.get('summary'):
                suggestions.append("Include a professional summary at the top")
            
            # Calculate basic ATS score
            score = 60  # Base score
            if resume_data.get('skills'): score += 10
            if resume_data.get('summary'): score += 10
            if len(numbers) >= 3: score += 10
            if action_verb_count >= 3: score += 10
            
            return {
                "ats_score": min(100, score),
                "improvements": suggestions[:5],
                "missing_keywords": missing_keywords,
                "formatting_issues": formatting_issues
            }
            
        except Exception as e:
            return {
                "ats_score": 70,
                "improvements": ["Ensure consistent formatting", "Add relevant keywords"],
                "missing_keywords": [],
                "formatting_issues": []
            }

    def analyze_job_posting(self, job_description: str) -> dict:
        """Analyze job posting using keyword extraction"""
        try:
            text_lower = job_description.lower()
            
            # Extract experience level
            experience_level = "mid"
            if any(term in text_lower for term in ["entry", "junior", "0-2 years"]):
                experience_level = "entry"
            elif any(term in text_lower for term in ["senior", "lead", "principal", "5+ years"]):
                experience_level = "senior"
            elif any(term in text_lower for term in ["executive", "director", "vp", "10+ years"]):
                experience_level = "executive"
            
            # Extract skills and requirements
            skill_keywords = []
            for category_skills in self.skill_categories.values():
                for skill in category_skills:
                    if skill.lower() in text_lower:
                        skill_keywords.append(skill)
            
            # Extract common requirements
            requirements = []
            if "degree" in text_lower or "bachelor" in text_lower:
                requirements.append("Bachelor's degree required")
            if "experience" in text_lower:
                requirements.append("Relevant work experience")
            if "certification" in text_lower:
                requirements.append("Professional certifications preferred")
            
            # Basic industry detection
            industry = "general"
            industry_keywords = {
                "technology": ["software", "tech", "IT", "development"],
                "finance": ["financial", "banking", "investment"],
                "healthcare": ["medical", "health", "clinical"],
                "education": ["teaching", "academic", "school"]
            }
            
            for ind, keywords in industry_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    industry = ind
                    break
            
            return {
                "required_skills": skill_keywords[:10],
                "preferred_skills": skill_keywords[5:10],
                "requirements": requirements,
                "experience_level": experience_level,
                "industry": industry,
                "keywords": self._extract_keywords_from_text(job_description)
            }
            
        except Exception as e:
            return {
                "required_skills": [],
                "preferred_skills": [],
                "requirements": [],
                "experience_level": "unknown",
                "industry": "general",
                "keywords": []
            }

    def generate_cover_letter(self, resume_data: dict, company_name: str, position_title: str, 
                             job_description: str = "", tone: str = "Professional") -> str:
        """Generate basic cover letter template"""
        try:
            name = resume_data.get('full_name', 'Applicant')
            
            # Extract key skills
            skills = resume_data.get('skills', [])[:3]
            skills_text = ', '.join(skills) if skills else "relevant professional skills"
            
            # Get most recent experience
            experience = resume_data.get('experience', [])
            recent_exp = ""
            if experience:
                exp = experience[0]
                recent_exp = f" In my recent role as {exp.get('job_title', 'a professional')} at {exp.get('company', 'my previous company')}, I have gained valuable experience that directly relates to this position."
            
            # Choose tone-appropriate language
            if tone.lower() == "enthusiastic":
                opening = f"I am excited to apply for the {position_title} position at {company_name}."
                closing = "I would be thrilled to contribute to your team's success."
            elif tone.lower() == "conservative":
                opening = f"I am writing to formally apply for the {position_title} position at {company_name}."
                closing = "I look forward to the opportunity to discuss my qualifications."
            else:  # Professional
                opening = f"I am writing to express my strong interest in the {position_title} position at {company_name}."
                closing = "I would welcome the opportunity to discuss how my background can contribute to your organization."
            
            cover_letter = f"""Dear Hiring Manager,

{opening} With my background in {skills_text}, I am confident that I would be a valuable addition to your team.{recent_exp}

My key qualifications include:
• Strong expertise in {skills[0] if skills else 'professional development'}
• Proven ability to deliver results in dynamic environments
• Excellent communication and collaboration skills
• Commitment to continuous learning and improvement

I am particularly drawn to {company_name} because of your reputation for innovation and excellence in the industry. I believe my skills and enthusiasm make me an ideal candidate for this role.

{closing}

Thank you for your consideration.

Sincerely,
{name}"""

            return cover_letter
            
        except Exception as e:
            return f"""Dear Hiring Manager,

I am writing to apply for the {position_title} position at {company_name}. I believe my background and skills make me a strong candidate for this role.

Thank you for your consideration.

Sincerely,
{resume_data.get('full_name', 'Applicant')}"""

    def _calculate_years_from_experience(self, experience: list) -> int:
        """Calculate total years from experience list"""
        if not experience:
            return 0
        
        total_months = 0
        for exp in experience:
            # Simple estimation: assume 2 years per job if no dates
            if exp.get('start_date') and exp.get('end_date'):
                try:
                    from datetime import datetime
                    start = datetime.fromisoformat(exp['start_date'])
                    end = datetime.fromisoformat(exp['end_date']) if not exp.get('is_current') else datetime.now()
                    months = (end.year - start.year) * 12 + (end.month - start.month)
                    total_months += max(0, months)
                except:
                    total_months += 24  # Default 2 years
            else:
                total_months += 24  # Default 2 years per experience
        
        return max(1, total_months // 12)

    def _extract_text_from_resume(self, resume_data: dict) -> str:
        """Extract all text from resume data"""
        text_parts = []
        
        # Add summary
        if resume_data.get('summary'):
            text_parts.append(resume_data['summary'])
        
        # Add experience
        for exp in resume_data.get('experience', []):
            text_parts.append(exp.get('description', ''))
        
        # Add skills
        if resume_data.get('skills'):
            text_parts.extend(resume_data['skills'])
        
        return ' '.join(text_parts)

    def _extract_keywords_from_text(self, text: str) -> list:
        """Extract important keywords from text"""
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
            'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'will',
            'with', 'have', 'from', 'they', 'know', 'want', 'been', 'good', 'much',
            'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long',
            'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Return unique keywords, limited to 15
        return list(set(keywords))[:15]