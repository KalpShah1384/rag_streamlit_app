import json
import os
import hashlib

USERS_FILE = "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def ensure_users_file():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)

def register_user(username, password):
    ensure_users_file()
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    
    if username in users:
        return False, "Username already exists."
    
    users[username] = hash_password(password)
    
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)
    return True, "Registration successful."

def verify_user(username, password):
    ensure_users_file()
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    
    if username not in users:
        return False, "User not found."
    
    if users[username] == hash_password(password):
        return True, "Login successful."
    else:
        return False, "Incorrect password."
