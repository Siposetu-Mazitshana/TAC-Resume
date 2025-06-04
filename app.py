
import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="TAC Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# THEN import other modules
import pandas as pd
from datetime import datetime
import json
from auth import authenticate_user, register_user, logout_user
# ... rest of imports
import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Import our modules
from auth import authenticate_user, register_user, logout_user
from database import init_database, get_user_resumes, save_resume_data, get_resume_data
from ai_services import generate_professional_summary, generate_job_description, get_content_suggestions
from resume_generator import ResumeGenerator
from export_utils import export_to_pdf, export_to_docx, export_to_html
from templates import get_available_templates, apply_template
from job_matcher import analyze_job_description, match_resume_to_job
from cover_letter import generate_cover_letter
from analytics import get_resume_analytics, track_resume_view
from collaboration import share_resume, get_shared_resumes
from linkedin_import import import_linkedin_profile
from utils import validate_email, sanitize_input

# Initialize the database
init_database()

# Configure the Streamlit page
st.set_page_config(
    page_title="TAC Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'guest_mode' not in st.session_state:
    st.session_state.guest_mode = False
if 'current_resume' not in st.session_state:
    st.session_state.current_resume = {}
if 'selected_template' not in st.session_state:
    st.session_state.selected_template = 'modern'

def show_login_page():
    """Display the login/registration page"""
    st.title("🚀 TAC Resume Builder")
    st.markdown("### AI-Powered Career Platform")
    
    # Guest mode option
    st.info("Try it out! You can continue as a guest to explore all features. Your data won't be saved.")
    if st.button("Continue as Guest", type="primary", use_container_width=True):
        st.session_state.authenticated = True
        st.session_state.user_id = None  # Guest user
        st.session_state.username = "Guest User"
        st.session_state.guest_mode = True
        st.success("Welcome! You're now using the app as a guest.")
        st.rerun()
    
    st.markdown("---")
    st.write("Or create an account to save your resumes:")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    user_id = authenticate_user(username, password)
                    if user_id:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            email = st.text_input("Email Address")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit_reg = st.form_submit_button("Register")
            
            if submit_reg:
                if new_username and email and new_password and confirm_password:
                    if not validate_email(email):
                        st.error("Please enter a valid email address")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        success = register_user(new_username, email, new_password)
                        if success:
                            st.success("Registration successful! Please login with your credentials.")
                        else:
                            st.error("Username or email already exists")
                else:
                    st.error("Please fill in all fields")

def show_dashboard():
    """Display the main dashboard"""
    if st.session_state.get('guest_mode', False):
        st.title(f"Welcome, {st.session_state.username}! 👋")
        st.info("You're in guest mode. Your data won't be saved. Create an account to save your resumes.")
    else:
        st.title(f"Welcome back, {st.session_state.username}! 👋")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.selectbox("Choose a section:", [
            "Dashboard",
            "Resume Builder", 
            "Job Matcher",
            "Cover Letter Generator",
            "Analytics",
            "Collaboration",
            "LinkedIn Import"
        ])
        
        st.divider()
        if st.button("Logout"):
            if not st.session_state.get('guest_mode', False):
                logout_user()
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.guest_mode = False
            st.rerun()
    
    if page == "Dashboard":
        show_dashboard_overview()
    elif page == "Resume Builder":
        show_resume_builder()
    elif page == "Job Matcher":
        show_job_matcher()
    elif page == "Cover Letter Generator":
        show_cover_letter_generator()
    elif page == "Analytics":
        show_analytics()
    elif page == "Collaboration":
        show_collaboration()
    elif page == "LinkedIn Import":
        show_linkedin_import()

def show_dashboard_overview():
    """Show dashboard overview with resume statistics"""
    col1, col2, col3 = st.columns(3)
    
    # Get user's resumes
    resumes = get_user_resumes(st.session_state.user_id)
    
    with col1:
        st.metric("Total Resumes", len(resumes))
    
    with col2:
        # Calculate total views from analytics
        total_views = sum([get_resume_analytics(resume['id'])['total_views'] for resume in resumes])
        st.metric("Total Views", total_views)
    
    with col3:
        shared_resumes = get_shared_resumes(st.session_state.user_id)
        st.metric("Shared Resumes", len(shared_resumes))
    
    st.divider()
    
    # Recent resumes
    st.subheader("Your Resumes")
    if resumes:
        for resume in resumes[:5]:  # Show latest 5
            with st.expander(f"📄 {resume['title']} - Created {resume['created_at'][:10]}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Edit", key=f"edit_{resume['id']}"):
                        st.session_state.current_resume = get_resume_data(resume['id'])
                        st.session_state.page = "Resume Builder"
                        st.rerun()
                with col2:
                    if st.button(f"Analytics", key=f"analytics_{resume['id']}"):
                        st.session_state.selected_resume_id = resume['id']
                        st.session_state.page = "Analytics"
                        st.rerun()
                with col3:
                    if st.button(f"Share", key=f"share_{resume['id']}"):
                        share_resume(resume['id'], "public")
                        st.success("Resume shared successfully!")
    else:
        st.info("No resumes yet. Create your first resume using the Resume Builder!")

def show_resume_builder():
    """Show the resume builder interface"""
    st.header("🎯 AI-Powered Resume Builder")
    
    # Template selection
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Choose Template")
        templates = get_available_templates()
        selected_template = st.selectbox("Template Style", list(templates.keys()))
        
        if selected_template != st.session_state.selected_template:
            st.session_state.selected_template = selected_template
            st.rerun()
        
        # Template preview
        st.markdown("**Template Preview:**")
        template_info = templates[selected_template]
        st.markdown(f"*{template_info['description']}*")
    
    with col2:
        st.subheader("Resume Content")
        
        # Resume building tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Personal Info", "Experience", "Education", "Skills", "Preview & Export"])
        
        with tab1:
            show_personal_info_form()
        
        with tab2:
            show_experience_form()
        
        with tab3:
            show_education_form()
        
        with tab4:
            show_skills_form()
        
        with tab5:
            show_preview_and_export()

def show_personal_info_form():
    """Personal information form"""
    st.subheader("Personal Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("Full Name", value=st.session_state.current_resume.get('full_name', ''))
        email = st.text_input("Email", value=st.session_state.current_resume.get('email', ''))
        phone = st.text_input("Phone", value=st.session_state.current_resume.get('phone', ''))
    
    with col2:
        location = st.text_input("Location", value=st.session_state.current_resume.get('location', ''))
        linkedin = st.text_input("LinkedIn URL", value=st.session_state.current_resume.get('linkedin', ''))
        website = st.text_input("Website/Portfolio", value=st.session_state.current_resume.get('website', ''))
    
    # Professional summary
    st.subheader("Professional Summary")
    summary = st.text_area("Professional Summary", 
                          value=st.session_state.current_resume.get('summary', ''),
                          height=150,
                          help="Describe your professional background and key achievements")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🤖 Generate AI Summary"):
            if full_name:
                ai_summary = generate_professional_summary(
                    name=full_name,
                    experience=st.session_state.current_resume.get('experience', []),
                    skills=st.session_state.current_resume.get('skills', [])
                )
                st.session_state.current_resume['summary'] = ai_summary
                st.rerun()
    
    # Save data
    if st.button("Save Personal Info"):
        st.session_state.current_resume.update({
            'full_name': sanitize_input(full_name),
            'email': sanitize_input(email),
            'phone': sanitize_input(phone),
            'location': sanitize_input(location),
            'linkedin': sanitize_input(linkedin),
            'website': sanitize_input(website),
            'summary': sanitize_input(summary)
        })
        st.success("Personal information saved!")

def show_experience_form():
    """Work experience form"""
    st.subheader("Work Experience")
    
    if 'experience' not in st.session_state.current_resume:
        st.session_state.current_resume['experience'] = []
    
    # Add new experience
    with st.expander("Add New Experience", expanded=False):
        with st.form("add_experience"):
            col1, col2 = st.columns(2)
            with col1:
                job_title = st.text_input("Job Title")
                company = st.text_input("Company")
                start_date = st.date_input("Start Date")
            with col2:
                location = st.text_input("Location")
                end_date = st.date_input("End Date")
                is_current = st.checkbox("Current Position")
            
            job_description = st.text_area("Job Description", height=150)
            
            submitted = st.form_submit_button("Add Experience")
            if submitted and job_title and company:
                new_experience = {
                    'job_title': sanitize_input(job_title),
                    'company': sanitize_input(company),
                    'location': sanitize_input(location),
                    'start_date': start_date.isoformat(),
                    'end_date': None if is_current else end_date.isoformat(),
                    'is_current': is_current,
                    'description': sanitize_input(job_description)
                }
                st.session_state.current_resume['experience'].append(new_experience)
                st.success("Experience added!")
                st.rerun()
    
    # Display existing experiences
    for i, exp in enumerate(st.session_state.current_resume.get('experience', [])):
        with st.expander(f"{exp['job_title']} at {exp['company']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Location:** {exp['location']}")
                st.write(f"**Duration:** {exp['start_date']} - {'Present' if exp['is_current'] else exp['end_date']}")
                st.write(f"**Description:** {exp['description']}")
            with col2:
                if st.button("🤖 Enhance", key=f"enhance_exp_{i}"):
                    enhanced_desc = generate_job_description(exp['job_title'], exp['description'])
                    st.session_state.current_resume['experience'][i]['description'] = enhanced_desc
                    st.rerun()
                if st.button("Remove", key=f"remove_exp_{i}"):
                    st.session_state.current_resume['experience'].pop(i)
                    st.rerun()

def show_education_form():
    """Education form"""
    st.subheader("Education")
    
    if 'education' not in st.session_state.current_resume:
        st.session_state.current_resume['education'] = []
    
    # Add new education
    with st.expander("Add Education", expanded=False):
        with st.form("add_education"):
            col1, col2 = st.columns(2)
            with col1:
                degree = st.text_input("Degree")
                institution = st.text_input("Institution")
                graduation_date = st.date_input("Graduation Date")
            with col2:
                field_of_study = st.text_input("Field of Study")
                gpa = st.text_input("GPA (optional)")
                location = st.text_input("Location")
            
            submitted = st.form_submit_button("Add Education")
            if submitted and degree and institution:
                new_education = {
                    'degree': sanitize_input(degree),
                    'institution': sanitize_input(institution),
                    'field_of_study': sanitize_input(field_of_study),
                    'graduation_date': graduation_date.isoformat(),
                    'gpa': sanitize_input(gpa),
                    'location': sanitize_input(location)
                }
                st.session_state.current_resume['education'].append(new_education)
                st.success("Education added!")
                st.rerun()
    
    # Display existing education
    for i, edu in enumerate(st.session_state.current_resume.get('education', [])):
        with st.expander(f"{edu['degree']} - {edu['institution']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Field:** {edu['field_of_study']}")
                st.write(f"**Graduated:** {edu['graduation_date']}")
                if edu['gpa']:
                    st.write(f"**GPA:** {edu['gpa']}")
                st.write(f"**Location:** {edu['location']}")
            with col2:
                if st.button("Remove", key=f"remove_edu_{i}"):
                    st.session_state.current_resume['education'].pop(i)
                    st.rerun()

def show_skills_form():
    """Skills form"""
    st.subheader("Skills & Competencies")
    
    if 'skills' not in st.session_state.current_resume:
        st.session_state.current_resume['skills'] = []
    
    # Add skills
    col1, col2 = st.columns([3, 1])
    with col1:
        new_skill = st.text_input("Add a skill")
    with col2:
        if st.button("Add Skill") and new_skill:
            skill = sanitize_input(new_skill)
            if skill not in st.session_state.current_resume['skills']:
                st.session_state.current_resume['skills'].append(skill)
                st.rerun()
    
    # AI suggestions
    if st.button("🤖 Get AI Skill Suggestions"):
        # Get job role from experience if available
        job_role = ""
        experience_list = st.session_state.current_resume.get('experience', [])
        if experience_list and len(experience_list) > 0:
            job_role = experience_list[0].get('job_title', '')
        
        suggestions = get_content_suggestions(
            job_role=job_role,
            content_type='skills'
        )
        if suggestions:
            st.write("**AI Suggested Skills:**")
            for suggestion in suggestions:
                if st.button(f"+ {suggestion}", key=f"add_skill_{suggestion}"):
                    if suggestion not in st.session_state.current_resume['skills']:
                        st.session_state.current_resume['skills'].append(suggestion)
                        st.rerun()
    
    # Display current skills
    if st.session_state.current_resume.get('skills'):
        st.write("**Current Skills:**")
        for i, skill in enumerate(st.session_state.current_resume['skills']):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"• {skill}")
            with col2:
                if st.button("×", key=f"remove_skill_{i}"):
                    st.session_state.current_resume['skills'].pop(i)
                    st.rerun()

def show_preview_and_export():
    """Preview and export functionality"""
    st.subheader("Resume Preview & Export")
    
    # Save resume
    col1, col2 = st.columns(2)
    with col1:
        resume_title = st.text_input("Resume Title", value="My Resume")
    with col2:
        if st.button("💾 Save Resume"):
            resume_id = save_resume_data(
                user_id=st.session_state.user_id,
                title=resume_title,
                data=st.session_state.current_resume,
                template=st.session_state.selected_template
            )
            st.success(f"Resume saved! ID: {resume_id}")
    
    # Preview
    st.subheader("Live Preview")
    generator = ResumeGenerator()
    preview_html = generator.generate_html_resume(
        st.session_state.current_resume,
        st.session_state.selected_template
    )
    st.markdown(preview_html, unsafe_allow_html=True)
    
    # Export options
    st.subheader("Export Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export PDF"):
            try:
                pdf_data = export_to_pdf(st.session_state.current_resume, st.session_state.selected_template)
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name=f"{resume_title}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF export failed: {str(e)}")
    
    with col2:
        if st.button("📝 Export DOCX"):
            try:
                docx_data = export_to_docx(st.session_state.current_resume, st.session_state.selected_template)
                st.download_button(
                    label="Download DOCX",
                    data=docx_data,
                    file_name=f"{resume_title}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"DOCX export failed: {str(e)}")
    
    with col3:
        if st.button("🌐 Export HTML"):
            html_data = export_to_html(st.session_state.current_resume, st.session_state.selected_template)
            st.download_button(
                label="Download HTML",
                data=html_data,
                file_name=f"{resume_title}.html",
                mime="text/html"
            )

def show_job_matcher():
    """Job matching functionality"""
    st.header("🎯 Job Matcher & ATS Optimizer")
    
    # Job description input
    st.subheader("Analyze Job Description")
    job_description = st.text_area("Paste job description here:", height=200)
    
    if st.button("🔍 Analyze Job Description") and job_description:
        analysis = analyze_job_description(job_description)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Key Requirements")
            for req in analysis.get('requirements', []):
                st.write(f"• {req}")
        
        with col2:
            st.subheader("Required Skills")
            for skill in analysis.get('skills', []):
                st.write(f"• {skill}")
    
    # Resume matching
    if st.session_state.current_resume and job_description:
        st.subheader("Resume Match Analysis")
        if st.button("🎯 Match My Resume"):
            match_result = match_resume_to_job(st.session_state.current_resume, job_description)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Match Score", f"{match_result['score']:.0%}")
            with col2:
                st.metric("Missing Skills", len(match_result.get('missing_skills', [])))
            with col3:
                st.metric("ATS Score", f"{match_result.get('ats_score', 0):.0%}")
            
            # Recommendations
            if match_result.get('recommendations'):
                st.subheader("Improvement Recommendations")
                for rec in match_result['recommendations']:
                    st.info(rec)

def show_cover_letter_generator():
    """Cover letter generation"""
    st.header("✍️ AI Cover Letter Generator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Job Details")
        company_name = st.text_input("Company Name")
        position_title = st.text_input("Position Title")
        job_description = st.text_area("Job Description", height=200)
    
    with col2:
        st.subheader("Customization")
        tone = st.selectbox("Tone", ["Professional", "Enthusiastic", "Conservative", "Creative"])
        length = st.selectbox("Length", ["Short", "Medium", "Long"])
        focus_areas = st.multiselect("Focus Areas", [
            "Technical Skills", "Leadership", "Problem Solving", 
            "Team Collaboration", "Innovation", "Customer Service"
        ])
    
    if st.button("🤖 Generate Cover Letter") and company_name and position_title:
        cover_letter = generate_cover_letter(
            resume_data=st.session_state.current_resume,
            company_name=company_name,
            position_title=position_title,
            job_description=job_description,
            tone=tone,
            length=length,
            focus_areas=focus_areas
        )
        
        st.subheader("Generated Cover Letter")
        st.text_area("Cover Letter", value=cover_letter, height=400)
        
        # Export cover letter
        st.download_button(
            label="Download Cover Letter",
            data=cover_letter,
            file_name=f"cover_letter_{company_name}_{position_title}.txt",
            mime="text/plain"
        )

def show_analytics():
    """Resume analytics dashboard"""
    st.header("📊 Resume Analytics")
    
    resumes = get_user_resumes(st.session_state.user_id)
    
    if not resumes:
        st.info("No resumes available for analytics. Create a resume first!")
        return
    
    selected_resume = st.selectbox("Select Resume", 
                                  options=[r['title'] for r in resumes])
    
    if selected_resume:
        resume_id = next(r['id'] for r in resumes if r['title'] == selected_resume)
        analytics_data = get_resume_analytics(resume_id)
        
        # Track this view
        track_resume_view(resume_id)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Views", analytics_data['total_views'])
        with col2:
            st.metric("Downloads", analytics_data['downloads'])
        with col3:
            st.metric("Shares", analytics_data['shares'])
        with col4:
            st.metric("Last Updated", analytics_data['last_updated'][:10])
        
        # View history chart
        if analytics_data.get('view_history'):
            st.subheader("View History")
            df = pd.DataFrame(analytics_data['view_history'])
            st.line_chart(df.set_index('date')['views'])

def show_collaboration():
    """Collaboration features"""
    st.header("🤝 Collaboration & Sharing")
    
    resumes = get_user_resumes(st.session_state.user_id)
    
    if not resumes:
        st.info("No resumes available for sharing. Create a resume first!")
        return
    
    # Share resume
    st.subheader("Share Resume")
    selected_resume = st.selectbox("Select Resume to Share", 
                                  options=[r['title'] for r in resumes])
    
    col1, col2 = st.columns(2)
    with col1:
        share_type = st.radio("Share Type", ["View Only", "Collaborative Edit"])
    with col2:
        expiry_days = st.number_input("Expiry (days)", min_value=1, max_value=365, value=30)
    
    if st.button("Generate Share Link"):
        resume_id = next(r['id'] for r in resumes if r['title'] == selected_resume)
        share_link = share_resume(resume_id, share_type.lower().replace(" ", "_"), expiry_days)
        st.success(f"Share link generated!")
        st.code(share_link)
    
    # View shared resumes
    st.subheader("Shared With You")
    shared_resumes = get_shared_resumes(st.session_state.user_id)
    
    for shared in shared_resumes:
        with st.expander(f"📄 {shared['title']} (shared by {shared['owner']})"):
            st.write(f"**Access Level:** {shared['access_level']}")
            st.write(f"**Shared Date:** {shared['shared_date']}")
            if st.button(f"View Resume", key=f"view_shared_{shared['id']}"):
                st.session_state.current_resume = get_resume_data(shared['resume_id'])
                st.rerun()

def show_linkedin_import():
    """LinkedIn profile import"""
    st.header("🔗 LinkedIn Profile Import")
    
    st.info("Import your LinkedIn profile data to quickly populate your resume.")
    
    linkedin_url = st.text_input("LinkedIn Profile URL", 
                                placeholder="https://www.linkedin.com/in/your-profile")
    
    if st.button("🔄 Import LinkedIn Data") and linkedin_url:
        try:
            linkedin_data = import_linkedin_profile(linkedin_url)
            
            if linkedin_data:
                st.success("LinkedIn data imported successfully!")
                
                # Merge with current resume
                if st.button("Merge with Current Resume"):
                    # Update current resume with LinkedIn data
                    st.session_state.current_resume.update(linkedin_data)
                    st.success("Data merged with current resume!")
                    st.rerun()
                
                # Preview imported data
                st.subheader("Imported Data Preview")
                st.json(linkedin_data)
            else:
                st.error("Failed to import LinkedIn data. Please check the URL and try again.")
        except Exception as e:
            st.error(f"Import failed: {str(e)}")

# Main application flow
def main():
    # Initialize database
    init_database()
    
    # Add logo to the application
    try:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("tac_logo.png", width=300)
    except:
        st.title("🤖 TAC Resume Builder")
    
    st.markdown("---")
    
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
