import bcrypt
import streamlit as st
from sqlalchemy.orm import Session
from backend.database.models import User
from backend.database.database import get_db
from typing import Optional, Dict, Any
import re

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        return True, "Password is valid"
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, full_name: str = None) -> Optional[User]:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return None
            
            # Create new user
            hashed_password = AuthService.hash_password(password)
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                full_name=full_name
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
            
        except Exception as e:
            db.rollback()
            st.error(f"Error creating user: {str(e)}")
            return None
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        try:
            # Find user by username or email
            user = db.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                return None
            
            if not user.is_active:
                return None
            
            if not AuthService.verify_password(password, user.hashed_password):
                return None
            
            return user
            
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return None
    
    @staticmethod
    def get_current_user() -> Optional[Dict[Any, Any]]:
        """Get current user from session state"""
        return st.session_state.get('user')
    
    @staticmethod
    def login_user(user: User):
        """Login user by storing in session state"""
        st.session_state['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'is_authenticated': True
        }
        st.session_state['authenticated'] = True
    
    @staticmethod
    def logout_user():
        """Logout user by clearing session state"""
        keys_to_remove = ['user', 'authenticated']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def require_auth():
        """Decorator/function to require authentication"""
        if not st.session_state.get('authenticated', False):
            st.error("Please login to access this feature")
            st.stop()
        return True