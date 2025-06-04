def get_available_templates() -> dict:
    """Return available resume templates with descriptions"""
    return {
        'modern': {
            'name': 'Modern',
            'description': 'Clean, contemporary design with accent colors',
            'best_for': 'Tech, Creative, Marketing roles'
        },
        'classic': {
            'name': 'Classic',
            'description': 'Traditional, professional layout',
            'best_for': 'Finance, Law, Consulting roles'
        },
        'creative': {
            'name': 'Creative',
            'description': 'Bold design with visual elements',
            'best_for': 'Design, Art, Media roles'
        },
        'minimal': {
            'name': 'Minimal',
            'description': 'Simple, clean layout focusing on content',
            'best_for': 'Academic, Research, Technical roles'
        },
        'professional': {
            'name': 'Professional',
            'description': 'Corporate-friendly design',
            'best_for': 'Management, Executive, Business roles'
        },
        'executive': {
            'name': 'Executive',
            'description': 'Sophisticated layout for senior positions',
            'best_for': 'C-level, VP, Director roles'
        }
    }

def get_template_html(template_name: str) -> str:
    """Return HTML template structure"""
    templates = {
        'modern': _get_modern_template(),
        'classic': _get_classic_template(),
        'creative': _get_creative_template(),
        'minimal': _get_minimal_template(),
        'professional': _get_professional_template(),
        'executive': _get_executive_template()
    }
    
    return templates.get(template_name, templates['modern'])

def get_template_styles(template_name: str) -> str:
    """Return CSS styles for template"""
    styles = {
        'modern': _get_modern_styles(),
        'classic': _get_classic_styles(),
        'creative': _get_creative_styles(),
        'minimal': _get_minimal_styles(),
        'professional': _get_professional_styles(),
        'executive': _get_executive_styles()
    }
    
    return styles.get(template_name, styles['modern'])

def _get_modern_template() -> str:
    """Modern template HTML structure"""
    return """
    <div class="resume-container">
        <header class="resume-header">
            <h1 class="name">{{full_name}}</h1>
            <div class="contact-info">
                <span class="email">{{email}}</span>
                <span class="phone">{{phone}}</span>
                <span class="location">{{location}}</span>
            </div>
            <div class="links">
                <a href="{{linkedin}}" class="linkedin">{{linkedin}}</a>
                <a href="{{website}}" class="website">{{website}}</a>
            </div>
        </header>
        
        <section class="summary">
            <h2>Professional Summary</h2>
            <p>{{summary}}</p>
        </section>
        
        <section class="experience">
            <h2>Professional Experience</h2>
            {{experience_section}}
        </section>
        
        <section class="education">
            <h2>Education</h2>
            {{education_section}}
        </section>
        
        <section class="skills">
            <h2>Skills</h2>
            <div class="skills-container">
                {{skills_section}}
            </div>
        </section>
    </div>
    """

def _get_modern_styles() -> str:
    """Modern template CSS styles"""
    return """
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        background: #f8f9fa;
    }
    
    .resume-container {
        max-width: 800px;
        margin: 20px auto;
        background: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 40px;
    }
    
    .resume-header {
        text-align: center;
        margin-bottom: 40px;
        padding-bottom: 20px;
        border-bottom: 3px solid #3498db;
    }
    
    .name {
        font-size: 2.5em;
        font-weight: 300;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    
    .contact-info {
        margin: 15px 0;
    }
    
    .contact-info span {
        margin: 0 15px;
        color: #7f8c8d;
    }
    
    .links a {
        color: #3498db;
        text-decoration: none;
        margin: 0 10px;
    }
    
    h2 {
        color: #2c3e50;
        font-size: 1.4em;
        margin: 30px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #ecf0f1;
    }
    
    .experience-item, .education-item {
        margin-bottom: 25px;
        padding: 15px;
        border-left: 4px solid #3498db;
        background: #f8f9fa;
    }
    
    .job-header h3 {
        color: #2c3e50;
        font-size: 1.2em;
        margin-bottom: 5px;
    }
    
    .company, .institution {
        font-weight: 600;
        color: #34495e;
    }
    
    .date-range {
        float: right;
        color: #7f8c8d;
        font-style: italic;
    }
    
    .job-location {
        color: #7f8c8d;
        margin-bottom: 10px;
    }
    
    .job-description {
        margin-left: 20px;
    }
    
    .job-description li {
        margin-bottom: 5px;
    }
    
    .skills-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    .skill-tag {
        background: #3498db;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.9em;
        display: inline-block;
    }
    
    .education-details {
        display: flex;
        justify-content: space-between;
        margin-top: 5px;
        color: #7f8c8d;
    }
    
    @media print {
        .resume-container {
            box-shadow: none;
            margin: 0;
        }
    }
    """

def _get_classic_template() -> str:
    """Classic template HTML structure"""
    return """
    <div class="resume-container">
        <header class="resume-header">
            <h1 class="name">{{full_name}}</h1>
            <div class="contact-info">
                {{email}} | {{phone}} | {{location}}
            </div>
            <div class="links">
                {{linkedin}} | {{website}}
            </div>
        </header>
        
        <section class="summary">
            <h2>OBJECTIVE</h2>
            <p>{{summary}}</p>
        </section>
        
        <section class="experience">
            <h2>EXPERIENCE</h2>
            {{experience_section}}
        </section>
        
        <section class="education">
            <h2>EDUCATION</h2>
            {{education_section}}
        </section>
        
        <section class="skills">
            <h2>SKILLS</h2>
            <p>{{skills_text}}</p>
        </section>
    </div>
    """

def _get_classic_styles() -> str:
    """Classic template CSS styles"""
    return """
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Times New Roman', serif;
        line-height: 1.5;
        color: #000;
        background: white;
    }
    
    .resume-container {
        max-width: 800px;
        margin: 20px auto;
        padding: 40px;
    }
    
    .resume-header {
        text-align: center;
        margin-bottom: 30px;
        padding-bottom: 15px;
        border-bottom: 2px solid #000;
    }
    
    .name {
        font-size: 2.2em;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }
    
    .contact-info {
        margin: 10px 0;
        font-size: 1.1em;
    }
    
    h2 {
        font-size: 1.2em;
        font-weight: bold;
        text-transform: uppercase;
        margin: 25px 0 10px 0;
        padding-bottom: 5px;
        border-bottom: 1px solid #000;
        letter-spacing: 1px;
    }
    
    .experience-item, .education-item {
        margin-bottom: 20px;
    }
    
    .job-header h3 {
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    
    .company, .institution {
        font-style: italic;
        margin-bottom: 5px;
    }
    
    .date-range {
        float: right;
        font-style: italic;
    }
    
    .job-description {
        margin-left: 20px;
        margin-top: 10px;
    }
    
    .education-details {
        font-style: italic;
    }
    
    @media print {
        .resume-container {
            margin: 0;
            padding: 20px;
        }
    }
    """

def _get_creative_template() -> str:
    """Creative template HTML structure"""
    return """
    <div class="resume-container">
        <aside class="sidebar">
            <div class="profile-section">
                <h1 class="name">{{full_name}}</h1>
                <div class="contact-info">
                    <div class="contact-item">📧 {{email}}</div>
                    <div class="contact-item">📱 {{phone}}</div>
                    <div class="contact-item">📍 {{location}}</div>
                    <div class="contact-item">🔗 {{linkedin}}</div>
                    <div class="contact-item">🌐 {{website}}</div>
                </div>
            </div>
            
            <section class="skills">
                <h2>Skills</h2>
                <div class="skills-container">
                    {{skills_section}}
                </div>
            </section>
        </aside>
        
        <main class="main-content">
            <section class="summary">
                <h2>About Me</h2>
                <p>{{summary}}</p>
            </section>
            
            <section class="experience">
                <h2>Experience</h2>
                {{experience_section}}
            </section>
            
            <section class="education">
                <h2>Education</h2>
                {{education_section}}
            </section>
        </main>
    </div>
    """

def _get_creative_styles() -> str:
    """Creative template CSS styles"""
    return """
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .resume-container {
        max-width: 1000px;
        margin: 20px auto;
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        display: flex;
    }
    
    .sidebar {
        width: 300px;
        background: linear-gradient(145deg, #2c3e50, #34495e);
        color: white;
        padding: 40px 30px;
    }
    
    .name {
        font-size: 1.8em;
        font-weight: 300;
        margin-bottom: 30px;
        text-align: center;
    }
    
    .contact-item {
        margin: 15px 0;
        font-size: 0.9em;
    }
    
    .sidebar h2 {
        color: #ecf0f1;
        font-size: 1.2em;
        margin: 30px 0 15px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .skill-tag {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 0.8em;
        display: inline-block;
        margin: 5px 5px 5px 0;
    }
    
    .main-content {
        flex: 1;
        padding: 40px;
    }
    
    .main-content h2 {
        color: #2c3e50;
        font-size: 1.4em;
        margin: 30px 0 15px 0;
        position: relative;
    }
    
    .main-content h2::after {
        content: '';
        position: absolute;
        bottom: -5px;
        left: 0;
        width: 50px;
        height: 3px;
        background: linear-gradient(45deg, #667eea, #764ba2);
    }
    
    .experience-item, .education-item {
        margin-bottom: 25px;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    
    .job-header h3 {
        color: #2c3e50;
        font-size: 1.2em;
        margin-bottom: 8px;
    }
    
    .company, .institution {
        color: #667eea;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .date-range {
        background: #667eea;
        color: white;
        padding: 2px 10px;
        border-radius: 10px;
        font-size: 0.8em;
        float: right;
    }
    
    @media print {
        body {
            background: white;
        }
        .resume-container {
            box-shadow: none;
        }
    }
    """

def _get_minimal_template() -> str:
    """Minimal template HTML structure"""
    return """
    <div class="resume-container">
        <header class="resume-header">
            <h1 class="name">{{full_name}}</h1>
            <div class="contact-info">
                {{email}} • {{phone}} • {{location}}
            </div>
        </header>
        
        <section class="summary">
            {{summary}}
        </section>
        
        <section class="experience">
            <h2>Experience</h2>
            {{experience_section}}
        </section>
        
        <section class="education">
            <h2>Education</h2>
            {{education_section}}
        </section>
        
        <section class="skills">
            <h2>Skills</h2>
            <p>{{skills_text}}</p>
        </section>
    </div>
    """

def _get_minimal_styles() -> str:
    """Minimal template CSS styles"""
    return """
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        background: white;
    }
    
    .resume-container {
        max-width: 700px;
        margin: 20px auto;
        padding: 40px;
    }
    
    .resume-header {
        margin-bottom: 40px;
    }
    
    .name {
        font-size: 2.5em;
        font-weight: 300;
        margin-bottom: 10px;
        color: #000;
    }
    
    .contact-info {
        color: #666;
        font-size: 1.1em;
    }
    
    h2 {
        font-size: 1.2em;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 30px 0 15px 0;
        color: #000;
    }
    
    .experience-item, .education-item {
        margin-bottom: 25px;
    }
    
    .job-header h3 {
        font-weight: 600;
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    
    .company, .institution {
        color: #666;
        margin-bottom: 5px;
    }
    
    .date-range {
        float: right;
        color: #999;
    }
    
    .job-description {
        margin: 10px 0;
    }
    
    .job-description li {
        margin-bottom: 3px;
        list-style: none;
        position: relative;
        padding-left: 15px;
    }
    
    .job-description li::before {
        content: '−';
        position: absolute;
        left: 0;
    }
    
    @media print {
        .resume-container {
            margin: 0;
            padding: 20px;
        }
    }
    """

def _get_professional_template() -> str:
    """Professional template HTML structure"""
    return """
    <div class="resume-container">
        <header class="resume-header">
            <div class="header-content">
                <h1 class="name">{{full_name}}</h1>
                <div class="contact-grid">
                    <div class="contact-item">{{email}}</div>
                    <div class="contact-item">{{phone}}</div>
                    <div class="contact-item">{{location}}</div>
                    <div class="contact-item">{{linkedin}}</div>
                </div>
            </div>
        </header>
        
        <section class="summary">
            <h2>Professional Profile</h2>
            <p>{{summary}}</p>
        </section>
        
        <section class="experience">
            <h2>Professional Experience</h2>
            {{experience_section}}
        </section>
        
        <section class="education">
            <h2>Education & Qualifications</h2>
            {{education_section}}
        </section>
        
        <section class="skills">
            <h2>Core Competencies</h2>
            <div class="skills-grid">
                {{skills_section}}
            </div>
        </section>
    </div>
    """

def _get_professional_styles() -> str:
    """Professional template CSS styles"""
    return """
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Georgia', serif;
        line-height: 1.6;
        color: #2c3e50;
        background: #f4f4f4;
    }
    
    .resume-container {
        max-width: 800px;
        margin: 20px auto;
        background: white;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .resume-header {
        background: #34495e;
        color: white;
        padding: 40px;
    }
    
    .name {
        font-size: 2.5em;
        font-weight: normal;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .contact-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        text-align: center;
    }
    
    .contact-item {
        background: rgba(255, 255, 255, 0.1);
        padding: 8px;
        border-radius: 5px;
    }
    
    .resume-container section {
        padding: 30px 40px;
    }
    
    h2 {
        color: #34495e;
        font-size: 1.4em;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
    }
    
    h2::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 0;
        width: 60px;
        height: 2px;
        background: #34495e;
    }
    
    .experience-item, .education-item {
        margin-bottom: 25px;
        padding: 20px 0;
        border-bottom: 1px solid #ecf0f1;
    }
    
    .job-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 10px;
    }
    
    .job-header h3 {
        color: #2c3e50;
        font-size: 1.2em;
        font-weight: 600;
    }
    
    .company, .institution {
        color: #7f8c8d;
        font-style: italic;
        margin-bottom: 10px;
    }
    
    .date-range {
        color: #95a5a6;
        font-weight: 500;
        background: #ecf0f1;
        padding: 5px 10px;
        border-radius: 3px;
    }
    
    .job-description {
        margin-top: 15px;
    }
    
    .job-description li {
        margin-bottom: 8px;
        color: #34495e;
    }
    
    .skills-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
    }
    
    .skill-tag {
        background: #ecf0f1;
        color: #2c3e50;
        padding: 8px 15px;
        text-align: center;
        border-radius: 5px;
        font-weight: 500;
    }
    
    @media print {
        .resume-container {
            box-shadow: none;
            margin: 0;
        }
    }
    """

def _get_executive_template() -> str:
    """Executive template HTML structure"""
    return """
    <div class="resume-container">
        <header class="resume-header">
            <div class="header-left">
                <h1 class="name">{{full_name}}</h1>
                <div class="title">Senior Executive</div>
            </div>
            <div class="header-right">
                <div class="contact-info">
                    <div>{{email}}</div>
                    <div>{{phone}}</div>
                    <div>{{location}}</div>
                </div>
            </div>
        </header>
        
        <section class="summary">
            <h2>Executive Summary</h2>
            <p>{{summary}}</p>
        </section>
        
        <section class="experience">
            <h2>Leadership Experience</h2>
            {{experience_section}}
        </section>
        
        <section class="education">
            <h2>Education & Credentials</h2>
            {{education_section}}
        </section>
        
        <section class="skills">
            <h2>Executive Competencies</h2>
            <div class="executive-skills">
                {{skills_section}}
            </div>
        </section>
    </div>
    """

def _get_executive_styles() -> str:
    """Executive template CSS styles"""
    return """
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Garamond', serif;
        line-height: 1.7;
        color: #1a1a1a;
        background: #f8f8f8;
    }
    
    .resume-container {
        max-width: 850px;
        margin: 20px auto;
        background: white;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid #e0e0e0;
    }
    
    .resume-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 50px 40px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    
    .name {
        font-size: 2.8em;
        font-weight: 300;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    
    .title {
        font-size: 1.2em;
        color: #b8d4f1;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .contact-info div {
        margin: 8px 0;
        text-align: right;
    }
    
    .resume-container section {
        padding: 35px 40px;
    }
    
    h2 {
        color: #1e3c72;
        font-size: 1.5em;
        margin-bottom: 25px;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        font-weight: 400;
    }
    
    h2::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 0;
        width: 80px;
        height: 3px;
        background: linear-gradient(45deg, #1e3c72, #2a5298);
    }
    
    .experience-item, .education-item {
        margin-bottom: 30px;
        padding: 25px;
        background: #fafafa;
        border-left: 5px solid #1e3c72;
    }
    
    .job-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 15px;
    }
    
    .job-header h3 {
        color: #1e3c72;
        font-size: 1.3em;
        font-weight: 600;
    }
    
    .company, .institution {
        color: #2a5298;
        font-weight: 600;
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    
    .date-range {
        color: #666;
        font-style: italic;
        background: white;
        padding: 8px 15px;
        border-radius: 20px;
        border: 1px solid #e0e0e0;
    }
    
    .job-description {
        margin-top: 15px;
        font-size: 1.05em;
    }
    
    .job-description li {
        margin-bottom: 10px;
        color: #333;
    }
    
    .executive-skills {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
    }
    
    .skill-tag {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        padding: 12px 20px;
        text-align: center;
        border-radius: 5px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9em;
    }
    
    @media print {
        .resume-container {
            box-shadow: none;
            border: none;
            margin: 0;
        }
    }
    """

def apply_template(resume_data: dict, template_name: str) -> dict:
    """Apply template-specific formatting to resume data"""
    formatted_data = resume_data.copy()
    
    # Template-specific customizations
    if template_name == 'executive':
        # For executive template, emphasize leadership aspects
        if formatted_data.get('experience'):
            for exp in formatted_data['experience']:
                # Add executive keywords if not present
                desc = exp.get('description', '')
                if any(keyword in desc.lower() for keyword in ['lead', 'manage', 'direct', 'oversee']):
                    exp['is_leadership'] = True
    
    elif template_name == 'creative':
        # For creative template, add visual emphasis to creative skills
        creative_skills = ['design', 'creative', 'visual', 'artistic', 'photography', 'graphic']
        if formatted_data.get('skills'):
            formatted_data['creative_skills'] = [
                skill for skill in formatted_data['skills']
                if any(creative_word in skill.lower() for creative_word in creative_skills)
            ]
    
    return formatted_data

def get_template_color_schemes() -> dict:
    """Return color scheme options for templates"""
    return {
        'blue': {
            'primary': '#3498db',
            'secondary': '#2c3e50',
            'accent': '#ecf0f1'
        },
        'green': {
            'primary': '#27ae60',
            'secondary': '#2c3e50',
            'accent': '#ecf0f1'
        },
        'purple': {
            'primary': '#9b59b6',
            'secondary': '#2c3e50',
            'accent': '#ecf0f1'
        },
        'red': {
            'primary': '#e74c3c',
            'secondary': '#2c3e50',
            'accent': '#ecf0f1'
        },
        'orange': {
            'primary': '#f39c12',
            'secondary': '#2c3e50',
            'accent': '#ecf0f1'
        },
        'dark': {
            'primary': '#34495e',
            'secondary': '#2c3e50',
            'accent': '#95a5a6'
        }
    }

def customize_template_colors(template_styles: str, color_scheme: dict) -> str:
    """Customize template colors based on selected scheme"""
    customized_styles = template_styles
    
    # Replace default colors with custom scheme
    customized_styles = customized_styles.replace('#3498db', color_scheme['primary'])
    customized_styles = customized_styles.replace('#2c3e50', color_scheme['secondary'])
    customized_styles = customized_styles.replace('#ecf0f1', color_scheme['accent'])
    
    return customized_styles
