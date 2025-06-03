import secrets
import json
from datetime import datetime, timedelta
import streamlit as st
from database import get_db_connection
from typing import Dict, List, Optional

def share_resume(resume_id: int, access_level: str = "view_only", 
                expiry_days: int = 30, shared_with_user_id: int = None) -> str:
    """Share a resume with specific access permissions"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate unique share token
        share_token = secrets.token_urlsafe(32)
        
        # Calculate expiry date
        expires_at = datetime.now() + timedelta(days=expiry_days)
        
        # Get the user who is sharing (from session)
        shared_by = st.session_state.get('user_id')
        
        if not shared_by:
            st.error("User not authenticated")
            return ""
        
        # Insert share record
        cursor.execute("""
            INSERT INTO resume_shares 
            (resume_id, shared_by, shared_with, access_level, share_token, expires_at, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (resume_id, shared_by, shared_with_user_id, access_level, 
              share_token, expires_at, datetime.now()))
        
        share_id = cursor.fetchone()[0]
        conn.commit()
        
        # Generate share link (in real app, this would be your domain)
        share_link = f"https://tacresumebuilder.app/shared/{share_token}"
        
        # Track sharing event
        from analytics import track_resume_share
        track_resume_share(resume_id, access_level, {
            'share_id': share_id,
            'expiry_days': expiry_days
        })
        
        return share_link
        
    except Exception as e:
        st.error(f"Failed to share resume: {str(e)}")
        return ""
    finally:
        if conn:
            conn.close()

def get_shared_resumes(user_id: int) -> List[Dict]:
    """Get resumes shared with a specific user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                rs.id, rs.resume_id, rs.access_level, rs.share_token, 
                rs.expires_at, rs.created_at as shared_date,
                r.title, r.template,
                u.username as owner
            FROM resume_shares rs
            JOIN resumes r ON rs.resume_id = r.id
            JOIN users u ON rs.shared_by = u.id
            WHERE (rs.shared_with = %s OR rs.shared_with IS NULL)
            AND rs.expires_at > NOW()
            ORDER BY rs.created_at DESC
        """, (user_id,))
        
        results = cursor.fetchall()
        shared_resumes = []
        
        for row in results:
            shared_resumes.append({
                'id': row[0],
                'resume_id': row[1],
                'access_level': row[2],
                'share_token': row[3],
                'expires_at': row[4].isoformat() if row[4] else None,
                'shared_date': row[5].isoformat() if row[5] else None,
                'title': row[6],
                'template': row[7],
                'owner': row[8]
            })
        
        return shared_resumes
        
    except Exception as e:
        st.error(f"Failed to get shared resumes: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def get_my_shared_resumes(user_id: int) -> List[Dict]:
    """Get resumes that I have shared with others"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                rs.id, rs.resume_id, rs.access_level, rs.share_token,
                rs.expires_at, rs.created_at as shared_date,
                r.title, r.template,
                u.username as shared_with_user
            FROM resume_shares rs
            JOIN resumes r ON rs.resume_id = r.id
            LEFT JOIN users u ON rs.shared_with = u.id
            WHERE rs.shared_by = %s
            ORDER BY rs.created_at DESC
        """, (user_id,))
        
        results = cursor.fetchall()
        my_shares = []
        
        for row in results:
            my_shares.append({
                'share_id': row[0],
                'resume_id': row[1],
                'access_level': row[2],
                'share_token': row[3],
                'expires_at': row[4].isoformat() if row[4] else None,
                'shared_date': row[5].isoformat() if row[5] else None,
                'title': row[6],
                'template': row[7],
                'shared_with_user': row[8] or 'Public Link'
            })
        
        return my_shares
        
    except Exception as e:
        st.error(f"Failed to get my shared resumes: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def revoke_share(share_id: int, user_id: int) -> bool:
    """Revoke a resume share"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify ownership before revoking
        cursor.execute("""
            DELETE FROM resume_shares 
            WHERE id = %s AND shared_by = %s
        """, (share_id, user_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        st.error(f"Failed to revoke share: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def validate_share_token(share_token: str) -> Optional[Dict]:
    """Validate a share token and return share details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                rs.id, rs.resume_id, rs.access_level, rs.expires_at,
                r.title, r.data, r.template,
                u.username as owner
            FROM resume_shares rs
            JOIN resumes r ON rs.resume_id = r.id
            JOIN users u ON rs.shared_by = u.id
            WHERE rs.share_token = %s
            AND rs.expires_at > NOW()
        """, (share_token,))
        
        result = cursor.fetchone()
        
        if result:
            return {
                'share_id': result[0],
                'resume_id': result[1],
                'access_level': result[2],
                'expires_at': result[3],
                'title': result[4],
                'data': json.loads(result[5]) if result[5] else {},
                'template': result[6],
                'owner': result[7]
            }
        
        return None
        
    except Exception as e:
        st.error(f"Failed to validate share token: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def create_collaboration_session(resume_id: int, collaborators: List[str], 
                                session_name: str = "") -> str:
    """Create a real-time collaboration session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        session_id = secrets.token_urlsafe(16)
        session_data = {
            'session_id': session_id,
            'resume_id': resume_id,
            'session_name': session_name or f"Collaboration Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'collaborators': collaborators,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        # Store collaboration session
        cursor.execute("""
            INSERT INTO resume_analytics (resume_id, event_type, event_data, created_at)
            VALUES (%s, %s, %s, %s)
        """, (resume_id, 'collaboration_session', json.dumps(session_data), datetime.now()))
        
        conn.commit()
        
        return session_id
        
    except Exception as e:
        st.error(f"Failed to create collaboration session: {str(e)}")
        return ""
    finally:
        if conn:
            conn.close()

def add_comment_to_resume(resume_id: int, user_id: int, comment_text: str, 
                         section: str = "", field: str = "") -> bool:
    """Add a comment to a specific section of a resume"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        comment_data = {
            'user_id': user_id,
            'comment': comment_text,
            'section': section,
            'field': field,
            'timestamp': datetime.now().isoformat(),
            'comment_id': secrets.token_urlsafe(8)
        }
        
        cursor.execute("""
            INSERT INTO resume_analytics (resume_id, event_type, event_data, created_at)
            VALUES (%s, %s, %s, %s)
        """, (resume_id, 'comment', json.dumps(comment_data), datetime.now()))
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Failed to add comment: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_resume_comments(resume_id: int) -> List[Dict]:
    """Get all comments for a resume"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ra.event_data, ra.created_at, u.username
            FROM resume_analytics ra
            LEFT JOIN users u ON (ra.event_data->>'user_id')::int = u.id
            WHERE ra.resume_id = %s 
            AND ra.event_type = 'comment'
            ORDER BY ra.created_at DESC
        """, (resume_id,))
        
        results = cursor.fetchall()
        comments = []
        
        for row in results:
            comment_data = json.loads(row[0]) if row[0] else {}
            comments.append({
                'comment_id': comment_data.get('comment_id', ''),
                'comment': comment_data.get('comment', ''),
                'section': comment_data.get('section', ''),
                'field': comment_data.get('field', ''),
                'timestamp': row[1].isoformat() if row[1] else '',
                'username': row[2] or 'Unknown User'
            })
        
        return comments
        
    except Exception as e:
        st.error(f"Failed to get comments: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def track_collaboration_activity(resume_id: int, user_id: int, activity_type: str, 
                               details: Dict = None):
    """Track collaboration activities"""
    try:
        activity_data = {
            'user_id': user_id,
            'activity_type': activity_type,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO resume_analytics (resume_id, event_type, event_data, created_at)
            VALUES (%s, %s, %s, %s)
        """, (resume_id, 'collaboration_activity', json.dumps(activity_data), datetime.now()))
        
        conn.commit()
        
    except Exception as e:
        st.error(f"Failed to track collaboration activity: {str(e)}")
    finally:
        if conn:
            conn.close()

def get_collaboration_history(resume_id: int) -> List[Dict]:
    """Get collaboration history for a resume"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ra.event_data, ra.created_at, u.username
            FROM resume_analytics ra
            LEFT JOIN users u ON (ra.event_data->>'user_id')::int = u.id
            WHERE ra.resume_id = %s 
            AND ra.event_type IN ('collaboration_activity', 'comment', 'share')
            ORDER BY ra.created_at DESC
            LIMIT 50
        """, (resume_id,))
        
        results = cursor.fetchall()
        history = []
        
        for row in results:
            activity_data = json.loads(row[0]) if row[0] else {}
            history.append({
                'activity': activity_data,
                'timestamp': row[1].isoformat() if row[1] else '',
                'username': row[2] or 'System'
            })
        
        return history
        
    except Exception as e:
        st.error(f"Failed to get collaboration history: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def suggest_improvements_collaboratively(resume_id: int, user_id: int, 
                                       suggestions: List[str]) -> bool:
    """Add improvement suggestions from collaborators"""
    try:
        suggestion_data = {
            'user_id': user_id,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat(),
            'suggestion_id': secrets.token_urlsafe(8)
        }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO resume_analytics (resume_id, event_type, event_data, created_at)
            VALUES (%s, %s, %s, %s)
        """, (resume_id, 'improvement_suggestion', json.dumps(suggestion_data), datetime.now()))
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Failed to add suggestions: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_improvement_suggestions(resume_id: int) -> List[Dict]:
    """Get improvement suggestions from collaborators"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ra.event_data, ra.created_at, u.username
            FROM resume_analytics ra
            LEFT JOIN users u ON (ra.event_data->>'user_id')::int = u.id
            WHERE ra.resume_id = %s 
            AND ra.event_type = 'improvement_suggestion'
            ORDER BY ra.created_at DESC
        """, (resume_id,))
        
        results = cursor.fetchall()
        suggestions = []
        
        for row in results:
            suggestion_data = json.loads(row[0]) if row[0] else {}
            suggestions.append({
                'suggestion_id': suggestion_data.get('suggestion_id', ''),
                'suggestions': suggestion_data.get('suggestions', []),
                'timestamp': row[1].isoformat() if row[1] else '',
                'username': row[2] or 'Anonymous'
            })
        
        return suggestions
        
    except Exception as e:
        st.error(f"Failed to get suggestions: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def create_review_request(resume_id: int, reviewer_emails: List[str], 
                         message: str = "", deadline: datetime = None) -> str:
    """Create a review request for a resume"""
    try:
        request_id = secrets.token_urlsafe(16)
        
        request_data = {
            'request_id': request_id,
            'resume_id': resume_id,
            'reviewer_emails': reviewer_emails,
            'message': message,
            'deadline': deadline.isoformat() if deadline else None,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO resume_analytics (resume_id, event_type, event_data, created_at)
            VALUES (%s, %s, %s, %s)
        """, (resume_id, 'review_request', json.dumps(request_data), datetime.now()))
        
        conn.commit()
        
        return request_id
        
    except Exception as e:
        st.error(f"Failed to create review request: {str(e)}")
        return ""
    finally:
        if conn:
            conn.close()

def get_pending_reviews(user_email: str) -> List[Dict]:
    """Get pending resume reviews for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ra.event_data, ra.created_at, r.title, u.username as requester
            FROM resume_analytics ra
            JOIN resumes r ON ra.resume_id = r.id
            JOIN users u ON r.user_id = u.id
            WHERE ra.event_type = 'review_request'
            AND ra.event_data->>'reviewer_emails' LIKE %s
            AND ra.event_data->>'status' = 'pending'
            ORDER BY ra.created_at DESC
        """, (f'%{user_email}%',))
        
        results = cursor.fetchall()
        reviews = []
        
        for row in results:
            review_data = json.loads(row[0]) if row[0] else {}
            reviews.append({
                'request_id': review_data.get('request_id', ''),
                'resume_id': review_data.get('resume_id', ''),
                'message': review_data.get('message', ''),
                'deadline': review_data.get('deadline', ''),
                'created_at': row[1].isoformat() if row[1] else '',
                'resume_title': row[2],
                'requester': row[3]
            })
        
        return reviews
        
    except Exception as e:
        st.error(f"Failed to get pending reviews: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def submit_review(request_id: str, reviewer_email: str, review_content: Dict) -> bool:
    """Submit a review for a resume"""
    try:
        review_data = {
            'request_id': request_id,
            'reviewer_email': reviewer_email,
            'review_content': review_content,
            'submitted_at': datetime.now().isoformat(),
            'review_id': secrets.token_urlsafe(8)
        }
        
        # Get the resume_id from the original request
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT resume_id FROM resume_analytics
            WHERE event_type = 'review_request'
            AND event_data->>'request_id' = %s
            LIMIT 1
        """, (request_id,))
        
        result = cursor.fetchone()
        if not result:
            return False
        
        resume_id = result[0]
        
        # Insert the review
        cursor.execute("""
            INSERT INTO resume_analytics (resume_id, event_type, event_data, created_at)
            VALUES (%s, %s, %s, %s)
        """, (resume_id, 'review_submission', json.dumps(review_data), datetime.now()))
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Failed to submit review: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_resume_reviews(resume_id: int) -> List[Dict]:
    """Get all reviews for a resume"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT event_data, created_at
            FROM resume_analytics
            WHERE resume_id = %s 
            AND event_type = 'review_submission'
            ORDER BY created_at DESC
        """, (resume_id,))
        
        results = cursor.fetchall()
        reviews = []
        
        for row in results:
            review_data = json.loads(row[0]) if row[0] else {}
            reviews.append({
                'review_id': review_data.get('review_id', ''),
                'reviewer_email': review_data.get('reviewer_email', ''),
                'review_content': review_data.get('review_content', {}),
                'submitted_at': row[1].isoformat() if row[1] else ''
            })
        
        return reviews
        
    except Exception as e:
        st.error(f"Failed to get reviews: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

