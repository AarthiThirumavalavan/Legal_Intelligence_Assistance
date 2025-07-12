import streamlit as st
import streamlit_authenticator as stauth
import yaml


print(f"auth.py loaded from: {__file__}")
print(f"Defined names: {dir()}")


try:
    with open("security/config.yaml") as f:
        config = yaml.safe_load(f)
        print("Printing config:", config)
except Exception as e:
    print("Failed loading config.yaml:", e)
    config = {}

cookie_config = config.get("cookie", {})
credentials = config.get("credentials", {})
preauthorized = config.get("preauthorized", {})
roles = config.get("roles", {})

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name=cookie_config.get("name", ""),
    key=cookie_config.get("key", ""),
    expiry_days=cookie_config.get("expiry_days", 1),
    preauthorized=preauthorized
)

def check_user_login():
    name, auth_status, username = authenticator.login("Login", "main")
    if auth_status:
        return {"name": name, "username": username, "role": roles.get(username, "viewer")}
    elif auth_status is False:
        st.error("Login failed.")
        return None
    else:
        return None
