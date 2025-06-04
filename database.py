import psycopg2
import json
import os
from datetime import datetime
import streamlit as st

# Database connection using environment variables
from urllib.parse import urlparse
import psycopg2
import os
import streamlit as st

def get_db_connection():
    """Create DB connection from DATABASE_URL (Render) or fallback env vars (local dev)"""
    try:
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            result = urlparse(db_url)
            conn = psycopg2.connect(
                dbname=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )
        else:
            # Local development fallback
            conn = psycopg2.connect(
                host=os.getenv("PGHOST", "localhost"),
                database=os.getenv("PGDATABASE", "tac_resume"),
                user=os.getenv("PGUSER", "postgres"),
                password=os.getenv("PGPASSWORD", ""),
                port=os.getenv("PGPORT", "5432")
            )
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        return None


def init_database():
    """Initialize database tables"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create resumes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                data JSONB NOT NULL,
                template VARCHAR(50) DEFAULT 'modern',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resume_analytics (
                id SERIAL PRIMARY KEY,
                resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
                event_type VARCHAR(50) NOT NULL,
                event_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create sharing table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resume_shares (
                id SERIAL PRIMARY KEY,
                resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
                shared_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
                shared_with INTEGER REFERENCES users(id) ON DELETE CASCADE,
                access_level VARCHAR(20) DEFAULT 'view_only',
                share_token VARCHAR(100) UNIQUE,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create job matches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_matches (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                job_description TEXT NOT NULL,
                match_score FLOAT,
                analysis_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create cover letters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cover_letters (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
                company_name VARCHAR(200),
                position_title VARCHAR(200),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def save_resume_data(user_id: int, title: str, data: dict, template: str = 'modern') -> int:
    """Save resume data to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO resumes (user_id, title, data, template, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, title, json.dumps(data), template, datetime.now()))
        
        resume_id = cursor.fetchone()[0]
        conn.commit()
        return resume_id
        
    except Exception as e:
        st.error(f"Error saving resume: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def get_resume_data(resume_id: int) -> dict:
    """Get resume data by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT data FROM resumes WHERE id = %s",
            (resume_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return json.loads(result[0])
        return {}
        
    except Exception as e:
        st.error(f"Error loading resume: {str(e)}")
        return {}
    finally:
        if conn:
            conn.close()

def get_user_resumes(user_id: int) -> list:
    """Get all resumes for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, template, created_at, updated_at
            FROM resumes 
            WHERE user_id = %s 
            ORDER BY updated_at DESC
        """, (user_id,))
        
        results = cursor.fetchall()
        resumes = []
        for result in results:
            resumes.append({
                'id': result[0],
                'title': result[1],
                'template': result[2],
                'created_at': result[3].isoformat() if result[3] else '',
                'updated_at': result[4].isoformat() if result[4] else ''
            })
        
        return resumes
        
    except Exception as e:
        st.error(f"Error loading resumes: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def update_resume_data(resume_id: int, title: str, data: dict, template: str) -> bool:
    """Update existing resume"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE resumes 
            SET title = %s, data = %s, template = %s, updated_at = %s
            WHERE id = %s
        """, (title, json.dumps(data), template, datetime.now(), resume_id))
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Error updating resume: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def delete_resume(resume_id: int, user_id: int) -> bool:
    """Delete a resume"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM resumes WHERE id = %s AND user_id = %s",
            (resume_id, user_id)
        )
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        st.error(f"Error deleting resume: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def save_analytics_event(resume_id: int, event_type: str, event_data: dict = None):
    """Save analytics event"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO resume_analytics (resume_id, event_type, event_data)
            VALUES (%s, %s, %s)
        """, (resume_id, event_type, json.dumps(event_data) if event_data else None))
        
        conn.commit()
        
    except Exception as e:
        st.error(f"Error saving analytics: {str(e)}")
    finally:
        if conn:
            conn.close()

def get_analytics_data(resume_id: int) -> dict:
    """Get analytics data for a resume"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get event counts
        cursor.execute("""
            SELECT event_type, COUNT(*) 
            FROM resume_analytics 
            WHERE resume_id = %s 
            GROUP BY event_type
        """, (resume_id,))
        
        events = dict(cursor.fetchall())
        
        # Get view history (last 30 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as views
            FROM resume_analytics 
            WHERE resume_id = %s AND event_type = 'view'
            AND created_at >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (resume_id,))
        
        view_history = [{'date': str(row[0]), 'views': row[1]} for row in cursor.fetchall()]
        
        return {
            'total_views': events.get('view', 0),
            'downloads': events.get('download', 0),
            'shares': events.get('share', 0),
            'view_history': view_history,
            'last_updated': datetime.now().isoformat()
        }
        
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
        return {}
    finally:
        if conn:
            conn.close()
