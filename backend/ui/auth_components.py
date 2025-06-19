import streamlit as st
from backend.services.auth_service import AuthService
from backend.database.database import SessionLocal
from backend.database.models import User

def render_login_form():
    """Render login form"""
    st.subheader("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if not username or not password:
                st.error("Please fill in all fields")
                return False
            
            db = SessionLocal()
            try:
                user = AuthService.authenticate_user(db, username, password)
                if user:
                    AuthService.login_user(user)
                    st.success(f"Welcome back, {user.full_name or user.username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    return False
            finally:
                db.close()
    
    return True

def render_signup_form():
    """Render signup form"""
    st.subheader("Create Account")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username")
            email = st.text_input("Email")
        
        with col2:
            full_name = st.text_input("Full Name (Optional)")
            password = st.text_input("Password", type="password")
        
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submit_button = st.form_submit_button("Create Account")
        
        if submit_button:
            # Validation
            if not username or not email or not password:
                st.error("Please fill in all required fields")
                return False
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return False
            
            if not AuthService.validate_email(email):
                st.error("Please enter a valid email address")
                return False
            
            is_valid, message = AuthService.validate_password(password)
            if not is_valid:
                st.error(message)
                return False
            
            # Create user
            db = SessionLocal()
            try:
                user = AuthService.create_user(db, username, email, password, full_name)
                if user:
                    st.success("Account created successfully! Please login.")
                    st.session_state['show_login'] = True
                    st.rerun()
                else:
                    st.error("Username or email already exists")
                    return False
            finally:
                db.close()
    
    return True

def render_auth_page():
    """Render main authentication page"""
    st.title("Welcome to AI Financial Advisor")
    
    # Initialize session state
    if 'show_login' not in st.session_state:
        st.session_state['show_login'] = True
    
    # Toggle between login and signup
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", use_container_width=True, 
                    type="primary" if st.session_state['show_login'] else "secondary"):
            st.session_state['show_login'] = True
            st.rerun()
    
    with col2:
        if st.button("Sign Up", use_container_width=True,
                    type="primary" if not st.session_state['show_login'] else "secondary"):
            st.session_state['show_login'] = False  
            st.rerun()
    
    st.markdown("---")
    
    # Show appropriate form
    if st.session_state['show_login']:
        render_login_form()
        
        st.markdown("---")
        st.markdown("Don't have an account? Click 'Sign Up' above.")
    else:
        render_signup_form()
        
        st.markdown("---")
        st.markdown("Already have an account? Click 'Login' above.")

def render_user_menu():
    """Render user menu for authenticated users"""
    current_user = AuthService.get_current_user()
    if not current_user:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.write(f"**Welcome, {current_user.get('full_name') or current_user.get('username')}!**")
        
        if st.button("Logout", use_container_width=True):
            AuthService.logout_user()
            st.rerun()

def check_authentication():
    """Check if user is authenticated, show auth page if not"""
    if not st.session_state.get('authenticated', False):
        render_auth_page()
        st.stop()
    else:
        render_user_menu()
        return True