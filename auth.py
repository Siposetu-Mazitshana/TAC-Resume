import hashlib
import secrets
import streamlit as st
from database import get_db_connection

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against its hash"""
    try:
        salt, password_hash = stored_hash.split(":")
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False

def authenticate_user(username: str, password: str) -> int:
    """Authenticate user and return user_id if successful"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, password_hash FROM users WHERE username = %s",
            (username,)
        )
        result = cursor.fetchone()
        
        if result and verify_password(password, result[1]):
            return result[0]  # Return user_id
        return None
        
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def register_user(username: str, email: str, password: str) -> bool:
    """Register a new user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username or email already exists
        cursor.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email)
        )
        if cursor.fetchone():
            return False  # User already exists
        
        # Create new user
        password_hash = hash_password(password)
        cursor.execute(
            """INSERT INTO users (username, email, password_hash, created_at) 
               VALUES (%s, %s, %s, NOW())""",
            (username, email, password_hash)
        )
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def logout_user():
    """Clear user session"""
    # Clear session state
    for key in list(st.session_state.keys()):
        if key.startswith('user_') or key in ['authenticated', 'username', 'current_resume']:
            del st.session_state[key]

def get_user_profile(user_id: int) -> dict:
    """Get user profile information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT username, email, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return {
                'username': result[0],
                'email': result[1],
                'created_at': result[2]
            }
        return {}
        
    except Exception as e:
        st.error(f"Profile error: {str(e)}")
        return {}
    finally:
        if conn:
            conn.close()

def update_user_profile(user_id: int, email: str = None, password: str = None) -> bool:
    """Update user profile"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if email:
            cursor.execute(
                "UPDATE users SET email = %s WHERE id = %s",
                (email, user_id)
            )
        
        if password:
            password_hash = hash_password(password)
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (password_hash, user_id)
            )
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Profile update error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()
