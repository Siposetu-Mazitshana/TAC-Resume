import json
import os
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import re
from typing import Dict, List, Tuple
from database import save_analytics_event

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_job_description(job_description: str) -> dict:
    """Analyze job description to extract key requirements and skills"""
    try:
        prompt = f"""
        Analyze this job description and extract key information in JSON format:
        
        Job Description:
        {job_description}
        
        Extract the following information:
        {{
            "required_skills": ["skill1", "skill2", "skill3"],
            "preferred_skills": ["skill1", "skill2"],
            "hard_requirements": ["requirement1", "requirement2"],
            "soft_requirements": ["requirement1", "requirement2"],
            "responsibilities": ["responsibility1", "responsibility2"],
            "keywords": ["keyword1", "keyword2", "keyword3"],
            "experience_level": "entry/mid/senior/executive",
            "education_requirements": ["degree requirement"],
            "industry": "industry_name",
            "company_size": "startup/small/medium/large/enterprise",
            "job_type": "full-time/part-time/contract/remote",
            "salary_range": "salary information if mentioned",
            "location": "job location"
        }}
        
        Be thorough and extract as much relevant information as possible.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert job analysis AI. Extract precise, relevant information from job descriptions."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=800
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        # Add word frequency analysis
        analysis['word_frequency'] = _analyze_word_frequency(job_description)
        analysis['ats_keywords'] = _extract_ats_keywords(job_description)
        
        return analysis
        
    except Exception as e:
        st.error(f"Job description analysis failed: {str(e)}")
        return {
            "required_skills": [],
            "preferred_skills": [],
            "hard_requirements": [],
            "soft_requirements": [],
            "responsibilities": [],
            "keywords": [],
            "experience_level": "unknown",
            "education_requirements": [],
            "industry": "unknown",
            "company_size": "unknown",
            "job_type": "unknown",
            "salary_range": "",
            "location": "",
            "word_frequency": {},
            "ats_keywords": []
        }

def match_resume_to_job(resume_data: dict, job_description: str) -> dict:
    """Match resume content to job requirements and provide scoring"""
    try:
        # First analyze the job description
        job_analysis = analyze_job_description(job_description)
        
        # Extract resume content for analysis
        resume_text = _extract_resume_text(resume_data)
        
        # Calculate various matching scores
        skill_match = _calculate_skill_match(resume_data, job_analysis)
        keyword_match = _calculate_keyword_match(resume_text, job_analysis)
        experience_match = _calculate_experience_match(resume_data, job_analysis)
        education_match = _calculate_education_match(resume_data, job_analysis)
        
        # Calculate overall match score
        overall_score = (
            skill_match['score'] * 0.35 +
            keyword_match['score'] * 0.25 +
            experience_match['score'] * 0.25 +
            education_match['score'] * 0.15
        )
        
        # Generate AI-powered recommendations
        recommendations = _generate_match_recommendations(
            resume_data, job_analysis, overall_score
        )
        
        # Calculate ATS compatibility score
        ats_score = _calculate_ats_score(resume_text, job_analysis)
        
        match_result = {
            'overall_score': overall_score,
            'score_breakdown': {
                'skills': skill_match['score'],
                'keywords': keyword_match['score'],
                'experience': experience_match['score'],
                'education': education_match['score']
            },
            'detailed_analysis': {
                'skill_match': skill_match,
                'keyword_match': keyword_match,
                'experience_match': experience_match,
                'education_match': education_match
            },
            'ats_score': ats_score,
            'recommendations': recommendations,
            'missing_skills': job_analysis['required_skills'],
            'matching_keywords': keyword_match.get('matching_keywords', []),
            'missing_keywords': keyword_match.get('missing_keywords', []),
            'job_analysis': job_analysis
        }
        
        return match_result
        
    except Exception as e:
        st.error(f"Resume matching failed: {str(e)}")
        return {
            'overall_score': 0.0,
            'score_breakdown': {},
            'ats_score': 0.0,
            'recommendations': ["Unable to analyze resume match. Please try again."],
            'missing_skills': [],
            'matching_keywords': [],
            'missing_keywords': []
        }

def _extract_resume_text(resume_data: dict) -> str:
    """Extract all text content from resume for analysis"""
    text_parts = []
    
    # Add summary
    if resume_data.get('summary'):
        text_parts.append(resume_data['summary'])
    
    # Add experience descriptions
    for exp in resume_data.get('experience', []):
        text_parts.append(exp.get('job_title', ''))
        text_parts.append(exp.get('company', ''))
        text_parts.append(exp.get('description', ''))
    
    # Add education
    for edu in resume_data.get('education', []):
        text_parts.append(edu.get('degree', ''))
        text_parts.append(edu.get('field_of_study', ''))
        text_parts.append(edu.get('institution', ''))
    
    # Add skills
    if resume_data.get('skills'):
        text_parts.extend(resume_data['skills'])
    
    return ' '.join(filter(None, text_parts))

def _calculate_skill_match(resume_data: dict, job_analysis: dict) -> dict:
    """Calculate how well resume skills match job requirements"""
    resume_skills = [skill.lower() for skill in resume_data.get('skills', [])]
    required_skills = [skill.lower() for skill in job_analysis.get('required_skills', [])]
    preferred_skills = [skill.lower() for skill in job_analysis.get('preferred_skills', [])]
    
    # Find matching skills
    matching_required = [skill for skill in required_skills if any(rs in skill or skill in rs for rs in resume_skills)]
    matching_preferred = [skill for skill in preferred_skills if any(rs in skill or skill in rs for rs in resume_skills)]
    
    # Calculate score
    required_score = len(matching_required) / len(required_skills) if required_skills else 1.0
    preferred_score = len(matching_preferred) / len(preferred_skills) if preferred_skills else 1.0
    
    # Weight required skills more heavily
    overall_score = (required_score * 0.7) + (preferred_score * 0.3)
    
    return {
        'score': min(1.0, overall_score),
        'matching_required': matching_required,
        'matching_preferred': matching_preferred,
        'missing_required': [skill for skill in required_skills if skill not in matching_required],
        'missing_preferred': [skill for skill in preferred_skills if skill not in matching_preferred],
        'total_matches': len(matching_required) + len(matching_preferred)
    }

def _calculate_keyword_match(resume_text: str, job_analysis: dict) -> dict:
    """Calculate keyword matching using TF-IDF similarity"""
    try:
        job_keywords = job_analysis.get('keywords', []) + job_analysis.get('ats_keywords', [])
        
        if not job_keywords:
            return {'score': 0.0, 'matching_keywords': [], 'missing_keywords': []}
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        
        # Combine resume and job keywords for analysis
        documents = [resume_text.lower(), ' '.join(job_keywords).lower()]
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Find specific keyword matches
        resume_lower = resume_text.lower()
        matching_keywords = [kw for kw in job_keywords if kw.lower() in resume_lower]
        missing_keywords = [kw for kw in job_keywords if kw.lower() not in resume_lower]
        
        return {
            'score': similarity,
            'matching_keywords': matching_keywords,
            'missing_keywords': missing_keywords,
            'keyword_density': len(matching_keywords) / len(job_keywords) if job_keywords else 0
        }
        
    except Exception as e:
        return {'score': 0.0, 'matching_keywords': [], 'missing_keywords': []}

def _calculate_experience_match(resume_data: dict, job_analysis: dict) -> dict:
    """Calculate experience level and relevance match"""
    experience_years = _calculate_total_experience(resume_data)
    required_level = job_analysis.get('experience_level', 'unknown').lower()
    
    # Map experience levels to years
    level_mapping = {
        'entry': (0, 2),
        'mid': (2, 5),
        'senior': (5, 10),
        'executive': (10, float('inf'))
    }
    
    score = 0.5  # Default neutral score
    
    if required_level in level_mapping:
        min_years, max_years = level_mapping[required_level]
        if min_years <= experience_years <= max_years:
            score = 1.0
        elif experience_years > max_years:
            # Overqualified but still good
            score = 0.9
        elif experience_years < min_years:
            # Under-qualified
            score = experience_years / min_years if min_years > 0 else 0.3
    
    # Check industry relevance
    industry_match = _check_industry_relevance(resume_data, job_analysis.get('industry', ''))
    
    return {
        'score': (score * 0.7) + (industry_match * 0.3),
        'years_experience': experience_years,
        'required_level': required_level,
        'level_match': score,
        'industry_relevance': industry_match
    }

def _calculate_education_match(resume_data: dict, job_analysis: dict) -> dict:
    """Calculate education requirements match"""
    education_requirements = job_analysis.get('education_requirements', [])
    user_education = resume_data.get('education', [])
    
    if not education_requirements:
        return {'score': 1.0, 'requirements_met': True}
    
    if not user_education:
        return {'score': 0.0, 'requirements_met': False}
    
    # Simple degree level matching
    degree_levels = {
        'high school': 1, 'diploma': 1, 'certificate': 1,
        'associate': 2, 'bachelor': 3, 'master': 4, 'mba': 4,
        'phd': 5, 'doctorate': 5
    }
    
    user_max_level = 0
    for edu in user_education:
        degree = edu.get('degree', '').lower()
        for level_name, level_value in degree_levels.items():
            if level_name in degree:
                user_max_level = max(user_max_level, level_value)
    
    required_level = 0
    for req in education_requirements:
        req_lower = req.lower()
        for level_name, level_value in degree_levels.items():
            if level_name in req_lower:
                required_level = max(required_level, level_value)
    
    score = min(1.0, user_max_level / required_level) if required_level > 0 else 1.0
    
    return {
        'score': score,
        'requirements_met': user_max_level >= required_level,
        'user_education_level': user_max_level,
        'required_level': required_level
    }

def _calculate_total_experience(resume_data: dict) -> float:
    """Calculate total years of professional experience"""
    from datetime import datetime
    
    total_months = 0
    
    for exp in resume_data.get('experience', []):
        start_date = exp.get('start_date')
        end_date = exp.get('end_date')
        
        if start_date:
            try:
                start = datetime.fromisoformat(start_date)
                if end_date and not exp.get('is_current', False):
                    end = datetime.fromisoformat(end_date)
                else:
                    end = datetime.now()
                
                months = (end.year - start.year) * 12 + (end.month - start.month)
                total_months += max(0, months)
            except:
                continue
    
    return round(total_months / 12, 1)

def _check_industry_relevance(resume_data: dict, target_industry: str) -> float:
    """Check if resume experience is relevant to target industry"""
    if not target_industry:
        return 1.0
    
    industry_keywords = {
        'technology': ['software', 'tech', 'programming', 'development', 'IT', 'computer'],
        'finance': ['financial', 'banking', 'investment', 'accounting', 'fintech'],
        'healthcare': ['medical', 'hospital', 'health', 'clinical', 'pharmaceutical'],
        'education': ['school', 'university', 'teaching', 'academic', 'education'],
        'retail': ['retail', 'sales', 'customer', 'store', 'commerce'],
        'manufacturing': ['manufacturing', 'production', 'factory', 'industrial'],
        'consulting': ['consulting', 'advisory', 'strategy', 'management']
    }
    
    target_keywords = industry_keywords.get(target_industry.lower(), [target_industry])
    resume_text = _extract_resume_text(resume_data).lower()
    
    matches = sum(1 for keyword in target_keywords if keyword in resume_text)
    return min(1.0, matches / len(target_keywords))

def _calculate_ats_score(resume_text: str, job_analysis: dict) -> float:
    """Calculate ATS (Applicant Tracking System) compatibility score"""
    score = 0.0
    total_checks = 5
    
    # Check 1: Keyword density
    keywords = job_analysis.get('keywords', []) + job_analysis.get('ats_keywords', [])
    if keywords:
        keyword_matches = sum(1 for kw in keywords if kw.lower() in resume_text.lower())
        score += (keyword_matches / len(keywords)) * 0.3
    else:
        score += 0.3
    
    # Check 2: Proper formatting indicators (basic text analysis)
    if len(resume_text) > 200:  # Sufficient content
        score += 0.2
    
    # Check 3: Standard section headers
    standard_headers = ['experience', 'education', 'skills', 'summary']
    header_matches = sum(1 for header in standard_headers if header in resume_text.lower())
    score += (header_matches / len(standard_headers)) * 0.2
    
    # Check 4: Quantifiable achievements (numbers in text)
    numbers = re.findall(r'\b\d+[%$]?\b', resume_text)
    if len(numbers) >= 3:
        score += 0.15
    elif len(numbers) >= 1:
        score += 0.1
    
    # Check 5: Action verbs
    action_verbs = ['managed', 'led', 'developed', 'created', 'improved', 'increased', 'decreased', 'implemented']
    verb_matches = sum(1 for verb in action_verbs if verb in resume_text.lower())
    if verb_matches >= 3:
        score += 0.15
    elif verb_matches >= 1:
        score += 0.1
    
    return min(1.0, score)

def _analyze_word_frequency(text: str) -> dict:
    """Analyze word frequency in job description"""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    word_freq = {}
    
    # Filter out common words
    stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'run', 'she', 'top', 'way', 'way', 'yes', 'yet'}
    
    for word in words:
        if word not in stop_words and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return top 20 most frequent words
    return dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20])

def _extract_ats_keywords(job_description: str) -> list:
    """Extract ATS-friendly keywords from job description"""
    # Technical skills patterns
    tech_patterns = [
        r'\b[A-Z]{2,}\b',  # Acronyms like SQL, API, AWS
        r'\b\w+(?:\.\w+)+\b',  # Technology names like React.js
        r'\b\w+\+{1,2}\b',  # Languages like C++
    ]
    
    keywords = []
    for pattern in tech_patterns:
        matches = re.findall(pattern, job_description)
        keywords.extend(matches)
    
    # Remove duplicates and return
    return list(set(keywords))

def _generate_match_recommendations(resume_data: dict, job_analysis: dict, overall_score: float) -> list:
    """Generate AI-powered recommendations for improving job match"""
    try:
        prompt = f"""
        Based on this resume analysis and job requirements, provide 5-7 specific, actionable recommendations 
        to improve the job application match score (current score: {overall_score:.1%}).
        
        Resume Summary: {resume_data.get('summary', 'No summary provided')}
        
        Job Requirements:
        - Required Skills: {', '.join(job_analysis.get('required_skills', []))}
        - Industry: {job_analysis.get('industry', 'Not specified')}
        - Experience Level: {job_analysis.get('experience_level', 'Not specified')}
        
        Current Resume Skills: {', '.join(resume_data.get('skills', []))}
        
        Provide recommendations in JSON format:
        {{
            "recommendations": [
                "specific recommendation 1",
                "specific recommendation 2",
                "specific recommendation 3"
            ]
        }}
        
        Focus on:
        - Missing skills to acquire or highlight
        - Resume content improvements
        - ATS optimization
        - Experience positioning
        - Keyword integration
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a career coach specializing in resume optimization and job matching."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=400
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('recommendations', [])
        
    except Exception as e:
        return [
            "Add more relevant keywords from the job description to your resume",
            "Quantify your achievements with specific numbers and metrics",
            "Ensure your skills section includes the required technical skills",
            "Tailor your professional summary to match the job requirements",
            "Include industry-specific terminology in your experience descriptions"
        ]

def get_job_match_insights(resume_data: dict, job_descriptions: list) -> dict:
    """Analyze resume against multiple job descriptions for insights"""
    try:
        insights = {
            'common_missing_skills': {},
            'strength_areas': {},
            'improvement_areas': [],
            'optimal_job_types': [],
            'skill_gaps': {}
        }
        
        match_results = []
        
        for job_desc in job_descriptions:
            match_result = match_resume_to_job(resume_data, job_desc)
            match_results.append(match_result)
        
        # Analyze patterns across multiple job matches
        all_missing_skills = []
        all_matching_skills = []
        
        for result in match_results:
            missing = result.get('detailed_analysis', {}).get('skill_match', {}).get('missing_required', [])
            matching = result.get('detailed_analysis', {}).get('skill_match', {}).get('matching_required', [])
            
            all_missing_skills.extend(missing)
            all_matching_skills.extend(matching)
        
        # Count frequency of missing skills
        for skill in all_missing_skills:
            insights['common_missing_skills'][skill] = insights['common_missing_skills'].get(skill, 0) + 1
        
        # Count frequency of matching skills (strengths)
        for skill in all_matching_skills:
            insights['strength_areas'][skill] = insights['strength_areas'].get(skill, 0) + 1
        
        # Calculate average scores
        avg_score = sum(r.get('overall_score', 0) for r in match_results) / len(match_results) if match_results else 0
        
        insights['average_match_score'] = avg_score
        insights['total_jobs_analyzed'] = len(job_descriptions)
        
        return insights
        
    except Exception as e:
        st.error(f"Job insights analysis failed: {str(e)}")
        return {}

def suggest_resume_improvements(resume_data: dict, target_role: str = "") -> dict:
    """Suggest specific improvements to resume based on analysis"""
    try:
        prompt = f"""
        Analyze this resume and suggest specific improvements for better job matching and ATS optimization.
        Target Role: {target_role}
        
        Resume Data:
        Summary: {resume_data.get('summary', 'None')}
        Skills: {', '.join(resume_data.get('skills', []))}
        Experience Count: {len(resume_data.get('experience', []))}
        Education Count: {len(resume_data.get('education', []))}
        
        Provide improvement suggestions in JSON format:
        {{
            "content_improvements": [
                "specific content suggestion 1",
                "specific content suggestion 2"
            ],
            "ats_improvements": [
                "ATS optimization suggestion 1",
                "ATS optimization suggestion 2"
            ],
            "skill_recommendations": [
                "skill to add or highlight 1",
                "skill to add or highlight 2"
            ],
            "formatting_suggestions": [
                "formatting improvement 1",
                "formatting improvement 2"
            ]
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume writer and career coach."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        return {
            "content_improvements": ["Add quantifiable achievements to your experience descriptions"],
            "ats_improvements": ["Include more industry-specific keywords"],
            "skill_recommendations": ["Consider adding relevant technical skills for your target role"],
            "formatting_suggestions": ["Use bullet points for better readability"]
        }

