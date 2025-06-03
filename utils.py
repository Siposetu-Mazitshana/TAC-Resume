import re
import html
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import streamlit as st
import hashlib
import secrets

def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def sanitize_input(text: Union[str, None]) -> str:
    """Sanitize user input to prevent XSS and other security issues"""
    if not text:
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Remove HTML tags and escape HTML entities
    text = html.escape(text)
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Limit length to prevent DoS
    return text[:5000].strip()

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    
    # Remove all non-digit characters except + for international numbers
    cleaned = re.sub(r'[^\d\+]', '', phone)
    
    # Check for valid phone number patterns
    patterns = [
        r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$',  # US format
        r'^\+?[1-9]\d{1,14}$',  # International format (E.164)
    ]
    
    return any(re.match(pattern, cleaned) for pattern in patterns)

def format_phone(phone: str) -> str:
    """Format phone number for display"""
    if not phone:
        return ""
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d\+]', '', phone)
    
    # Format US numbers
    if len(cleaned) == 10:
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    elif len(cleaned) == 11 and cleaned.startswith('1'):
        return f"({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
    
    # Return as-is for international numbers
    return cleaned

def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return False
    
    url_pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(url_pattern, url))

def format_date(date_string: str, format_type: str = "display") -> str:
    """Format date string for display or storage"""
    if not date_string:
        return ""
    
    try:
        # Parse the date
        if isinstance(date_string, str):
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%Y-%m', '%m/%d/%Y', '%m-%d-%Y']:
                try:
                    date_obj = datetime.strptime(date_string, fmt)
                    break
                except ValueError:
                    continue
            else:
                return date_string  # Return original if can't parse
        else:
            date_obj = date_string
        
        # Format based on type
        if format_type == "display":
            return date_obj.strftime("%B %Y")  # "January 2023"
        elif format_type == "short":
            return date_obj.strftime("%m/%Y")  # "01/2023"
        elif format_type == "iso":
            return date_obj.strftime("%Y-%m-%d")  # "2023-01-01"
        else:
            return date_obj.strftime("%Y-%m-%d")
            
    except Exception:
        return date_string

def calculate_experience_duration(start_date: str, end_date: str = None, is_current: bool = False) -> str:
    """Calculate duration between two dates"""
    if not start_date:
        return ""
    
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        
        if is_current or not end_date:
            end = datetime.now()
        else:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        
        duration = end - start
        
        # Calculate years and months
        years = duration.days // 365
        months = (duration.days % 365) // 30
        
        if years > 0:
            if months > 0:
                return f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}"
            else:
                return f"{years} year{'s' if years != 1 else ''}"
        elif months > 0:
            return f"{months} month{'s' if months != 1 else ''}"
        else:
            return "Less than 1 month"
            
    except Exception:
        return ""

def clean_text(text: str, max_length: int = None) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Convert to string and strip whitespace
    text = str(text).strip()
    
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # Remove non-printable characters
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + "..."
    
    return text

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text"""
    if not text:
        return []
    
    # Convert to lowercase and extract words
    words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + ',}\b', text.lower())
    
    # Common stop words to exclude
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
        'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy',
        'did', 'man', 'run', 'she', 'top', 'way', 'yes', 'yet', 'with', 'have',
        'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time',
        'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many',
        'over', 'such', 'take', 'than', 'them', 'well', 'were'
    }
    
    # Filter out stop words and duplicates
    keywords = list(set(word for word in words if word not in stop_words))
    
    return sorted(keywords)

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)

def hash_string(text: str, salt: str = "") -> str:
    """Create a hash of a string with optional salt"""
    return hashlib.sha256((text + salt).encode()).hexdigest()

def validate_json(json_string: str) -> tuple[bool, dict]:
    """Validate JSON string and return parsed object"""
    try:
        parsed = json.loads(json_string)
        return True, parsed
    except json.JSONDecodeError as e:
        return False, {"error": str(e)}

def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """Safely get value from dictionary with dot notation support"""
    if not isinstance(dictionary, dict):
        return default
    
    keys = key.split('.')
    value = dictionary
    
    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts (simple Jaccard similarity)"""
    if not text1 or not text2:
        return 0.0
    
    # Convert to sets of words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def format_currency(amount: Union[int, float, str], currency: str = "USD") -> str:
    """Format currency amount"""
    try:
        amount = float(amount)
        if currency.upper() == "USD":
            return f"${amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    except (ValueError, TypeError):
        return str(amount)

def validate_date_range(start_date: str, end_date: str) -> bool:
    """Validate that end_date is after start_date"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return end >= start
    except ValueError:
        return False

def get_age_from_date(birth_date: str) -> Optional[int]:
    """Calculate age from birth date"""
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return age if age >= 0 else None
    except ValueError:
        return None

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text"""
    if not text:
        return ""
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    return text.strip()

def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text"""
    if not text:
        return []
    
    # Find all number patterns including decimals, percentages, currency
    number_pattern = r'-?\d+(?:\.\d+)?'
    matches = re.findall(number_pattern, text)
    
    try:
        return [float(match) for match in matches]
    except ValueError:
        return []

def is_business_email(email: str) -> bool:
    """Check if email is likely a business email (not personal)"""
    if not validate_email(email):
        return False
    
    domain = email.split('@')[1].lower()
    
    # Common personal email domains
    personal_domains = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'aol.com', 'icloud.com', 'live.com', 'msn.com'
    }
    
    return domain not in personal_domains

def generate_filename(base_name: str, extension: str = "", timestamp: bool = True) -> str:
    """Generate a safe filename"""
    # Remove unsafe characters
    safe_name = re.sub(r'[^\w\-_\.]', '_', base_name)
    
    # Add timestamp if requested
    if timestamp:
        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{safe_name}_{time_str}"
    
    # Add extension if provided
    if extension and not extension.startswith('.'):
        extension = f".{extension}"
    
    return f"{safe_name}{extension}"

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def merge_dicts(*dicts: dict) -> dict:
    """Merge multiple dictionaries, with later ones taking precedence"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result

def get_file_size_str(size_bytes: int) -> str:
    """Convert file size in bytes to human readable string"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def debounce_function(wait_time: float = 1.0):
    """Decorator to debounce function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Simple debouncing using session state
            key = f"debounce_{func.__name__}"
            last_call = st.session_state.get(f"{key}_last_call", 0)
            current_time = datetime.now().timestamp()
            
            if current_time - last_call >= wait_time:
                st.session_state[f"{key}_last_call"] = current_time
                return func(*args, **kwargs)
            
        return wrapper
    return decorator

def validate_password_strength(password: str) -> Dict[str, Union[bool, str, int]]:
    """Validate password strength and return detailed feedback"""
    if not password:
        return {
            'is_strong': False,
            'score': 0,
            'feedback': 'Password is required'
        }
    
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 2
    else:
        feedback.append("Password should be at least 8 characters long")
    
    # Uppercase check
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Include at least one uppercase letter")
    
    # Lowercase check
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Include at least one lowercase letter")
    
    # Number check
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Include at least one number")
    
    # Special character check
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Include at least one special character")
    
    # Length bonus
    if len(password) >= 12:
        score += 1
    
    return {
        'is_strong': score >= 4,
        'score': min(5, score),
        'feedback': '; '.join(feedback) if feedback else 'Password is strong'
    }

