# security/auth.py

import bcrypt
import yaml
from pathlib import Path
import streamlit as st

CONFIG_PATH = Path("config.yaml")

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return None

def authenticate_user(username: str, password: str):
    config = load_config()
    if not config:
        return False, None

    users = config.get("credentials", {}).get("usernames", {})
    roles = config.get("roles", {})

    if username not in users:
        return False, None

    stored_hash = users[username].get("password", "")
    if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return False, None

    user_info = {
        "username": username,
        "name": users[username].get("name", ""),
        "email": users[username].get("email", ""),
        "role": roles.get(username, "user")
    }

    return True, user_info

def check_user_login():
    if "authenticated" in st.session_state and st.session_state.authenticated:
        return st.session_state.get("user_info")

    st.title("JUSTIA Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("🔐 Login"):
        success, user_info = authenticate_user(username, password)
        if success:
            st.session_state.authenticated = True
            st.session_state.user_info = user_info
            st.success(f"Welcome, {user_info['name']}!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    return None

def logout_user():
    st.session_state.authenticated = False
    st.session_state.user_info = {}
    st.success("👋 You have been logged out.")
    st.rerun()

def get_user_permissions(role):
    default_perms = {
        "admin": ["manage_users", "view_logs", "access_all_tools"],
        "lawyer": ["case_templates", "legal_research"],
        "paralegal": ["document_review", "basic_research"],
        "analyst": ["view_reports"]
    }
    return default_perms.get(role, [])

def is_role_authorized(user_info, required_roles):
    return user_info and user_info.get("role") in required_roles

def check_permission(user_info, permission):
    return permission in get_user_permissions(user_info.get("role", ""))
