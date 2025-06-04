from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Analyze job description to extract top keywords
def analyze_job_description(job_description):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([job_description])
    keywords = vectorizer.get_feature_names_out()
    return keywords[:10].tolist()  # Return top 10 keywords

# Match resume content to job description using cosine similarity
def match_resume_to_job(resume_text, job_description):
    documents = [resume_text, job_description]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    match_score = round(similarity[0][0] * 100, 2)  # Convert to percentage

    return match_score
