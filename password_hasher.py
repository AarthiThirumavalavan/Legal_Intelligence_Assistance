#!/usr/bin/env python3
"""
Complete User Management Tool for JUSTIA Authentication
This script helps you create users, hash passwords, and update config.yaml
"""

import bcrypt
import getpass
import yaml
import os
from pathlib import Path

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def load_config():
    """Load existing config.yaml or create a new one"""
    config_path = Path("security/config.yaml")
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            print(f"✅ Loaded existing config from {config_path}")
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            config = create_default_config()
    else:
        print("📝 Config file doesn't exist. Creating new one...")
        config = create_default_config()
    
    return config, config_path

def create_default_config():
    """Create a default config structure"""
    return {
        'credentials': {
            'usernames': {}
        },
        'cookie': {
            'name': 'justia_auth_cookie',
            'key': 'your_secret_key_here_make_it_long_and_random_123456789',
            'expiry_days': 7
        },
        'preauthorized': {
            'emails': []
        },
        'roles': {}
    }

def save_config(config, config_path):
    """Save config to file"""
    try:
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        print(f"✅ Config saved to {config_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False

def get_user_input():
    """Get user details from input"""
    print("\n" + "="*60)
    print("📝 Enter User Details")
    print("="*60)
    
    while True:
        username = input("Username: ").strip()
        if username:
            break
        print("❌ Username cannot be empty!")
    
    while True:
        name = input("Full Name: ").strip()
        if name:
            break
        print("❌ Full name cannot be empty!")
    
    while True:
        email = input("Email: ").strip()
        if email and "@" in email:
            break
        print("❌ Please enter a valid email address!")
    
    while True:
        password = getpass.getpass("Password: ")
        if password:
            confirm_password = getpass.getpass("Confirm Password: ")
            if password == confirm_password:
                break
            else:
                print("❌ Passwords don't match! Try again.")
        else:
            print("❌ Password cannot be empty!")
    
    # Define ONLY allowed roles - no custom roles allowed
    allowed_roles = ["admin", "lawyer", "paralegal", "analyst"]
    
    print(f"Allowed roles: {', '.join(allowed_roles)}")
    while True:
        role = input("Role: ").strip().lower()
        if not role:
            print("❌ Role cannot be empty!")
            continue
        
        if role in allowed_roles:
            break
        else:
            print(f"❌ Access Denied! Role '{role}' is not authorized.")
            print(f"❌ Only these roles are allowed: {', '.join(allowed_roles)}")
            print("❌ Please contact an administrator if you need access.")
    
    return {
        'username': username,
        'name': name,
        'email': email,
        'password': password,
        'role': role
    }

def display_user_info(user_data, hashed_password):
    """Display user information"""
    print("\n" + "="*60)
    print("👤 User Information")
    print("="*60)
    print(f"Username: {user_data['username']}")
    print(f"Full Name: {user_data['name']}")
    print(f"Email: {user_data['email']}")
    print(f"Role: {user_data['role']}")
    print(f"Password: {user_data['password']}")
    print(f"Hashed Password: {hashed_password}")
    print("="*60)
    
    # Verify hash
    if verify_password(user_data['password'], hashed_password):
        print("✅ Password hash verification successful!")
    else:
        print("❌ Password hash verification failed!")

def add_user_to_config(config, user_data, hashed_password):
    """Add user to config"""
    username = user_data['username']
    
    # Check if user already exists
    if username in config['credentials']['usernames']:
        overwrite = input(f"⚠️  User '{username}' already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ User not added.")
            return config
    
    # Add user to credentials
    config['credentials']['usernames'][username] = {
        'name': user_data['name'],
        'email': user_data['email'],
        'password': hashed_password
    }
    
    # Add email to preauthorized if not already there
    if user_data['email'] not in config['preauthorized']['emails']:
        config['preauthorized']['emails'].append(user_data['email'])
    
    # Add role
    config['roles'][username] = user_data['role']
    
    print(f"✅ User '{username}' added to config!")
    return config

def list_existing_users(config):
    """List existing users in config"""
    users = config.get('credentials', {}).get('usernames', {})
    if not users:
        print("📝 No users found in config.")
        return
    
    print("\n" + "="*60)
    print("👥 Existing Users")
    print("="*60)
    for username, user_info in users.items():
        role = config.get('roles', {}).get(username, 'user')
        print(f"• {username} ({user_info['name']}) - {user_info['email']} [{role}]")
    print("="*60)

def main():
    print("🔐 JUSTIA User Management Tool")
    print("=" * 60)
    
    # Load existing config
    config, config_path = load_config()
    
    while True:
        print("\n📋 Options:")
        print("1. Add new user")
        print("2. List existing users")
        print("3. Hash password only")
        print("4. Quit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            # Add new user
            user_data = get_user_input()
            hashed_password = hash_password(user_data['password'])
            
            display_user_info(user_data, hashed_password)
            
            # Ask if they want to add to config
            add_to_config = input("\n💾 Add this user to config.yaml? (Y/n): ").strip().lower()
            if add_to_config != 'n':
                config = add_user_to_config(config, user_data, hashed_password)
                
                # Save config
                save_config(config, config_path)
                print(f"✅ User '{user_data['username']}' has been added to config!")
            else:
                print("📋 User information generated but not saved to config.")
        
        elif choice == '2':
            # List existing users
            list_existing_users(config)
        
        elif choice == '3':
            # Hash password only
            password = getpass.getpass("Enter password to hash: ")
            if password:
                hashed = hash_password(password)
                print(f"\nOriginal password: {password}")
                print(f"Hashed password: {hashed}")
                
                if verify_password(password, hashed):
                    print("✅ Hash verification successful!")
                else:
                    print("❌ Hash verification failed!")
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please select 1-4.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")