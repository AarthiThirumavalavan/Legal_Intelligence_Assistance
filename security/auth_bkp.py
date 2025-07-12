import streamlit as st
import hashlib
import json
import os

# Example of how your auth.py should handle the login form
def check_user_login():
    """
    Check if user is logged in, show login form if not
    Returns user dict if authenticated, None if not
    """
    # Check if user is already logged in
    if 'user' in st.session_state and st.session_state.user:
        return st.session_state.user
    
    # Show login form
    st.title("🔐 JUSTIA Login")
    
    # Use a proper form with location specified
    with st.form("login_form", clear_on_submit=False):
        st.subheader("Please log in to continue")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        # Submit button
        login_button = st.form_submit_button("Login", type="primary")
        
        if login_button:
            if username and password:
                # Authenticate user
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome, {user['name']}!")
                    st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")
    
    return None

def authenticate_user(username, password):
    """
    Authenticate user against your user database
    Returns user dict if valid, None if invalid
    """
    # This is a simple example - replace with your actual authentication logic
    users = load_users()  # Load from your user database
    
    for user in users:
        if user['username'] == username and verify_password(password, user['password_hash']):
            return {
                'id': user['id'],
                'username': user['username'],
                'name': user['name'],
                'role': user['role']
            }
    
    return None

def load_users():
    """Load users from your database/file"""
    # Example - replace with your actual user loading logic
    users_file = "users.json"
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            return json.load(f)
    return []

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

def logout_user():
    """Log out the current user"""
    if 'user' in st.session_state:
        del st.session_state.user
    st.rerun()

def get_user_permissions(role):
    """Get permissions for a given role"""
    permissions = {
        'admin': ['manage_users', 'view_logs', 'full_access', 'case_management'],
        'lawyer': ['case_management', 'legal_research', 'document_creation'],
        'paralegal': ['document_review', 'basic_research', 'case_support']
    }
    return permissions.get(role, [])

def check_permission(user, permission):
    """Check if user has a specific permission"""
    user_permissions = get_user_permissions(user['role'])
    return permission in user_permissions

def is_role_authorized(user, required_roles):
    """Check if user's role is in the list of required roles"""
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    return user['role'] in required_roles