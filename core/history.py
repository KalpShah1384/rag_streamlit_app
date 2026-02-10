import json
import os
from datetime import datetime
import uuid

CHATS_DIR = "chats"

def ensure_chats_dir():
    if not os.path.exists(CHATS_DIR):
        os.makedirs(CHATS_DIR)

def save_chat(chat_id, messages, title=None):
    ensure_chats_dir()
    if not title and messages:
        # Use the first 30 chars of the first user message as title
        first_user_msg = next((m["content"] for m in messages if m["role"] == "user"), "New Chat")
        title = first_user_msg[:30] + "..." if len(first_user_msg) > 30 else first_user_msg

    chat_data = {
        "id": chat_id,
        "title": title or "New Chat",
        "updated_at": datetime.now().isoformat(),
        "messages": messages
    }
    
    file_path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=4)

def load_chat(chat_id):
    file_path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def list_chats():
    ensure_chats_dir()
    chats = []
    for filename in os.listdir(CHATS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(CHATS_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    chats.append({
                        "id": data["id"],
                        "title": data["title"],
                        "updated_at": data["updated_at"]
                    })
            except Exception:
                continue
    # Sort by updated_at descending
    return sorted(chats, key=lambda x: x["updated_at"], reverse=True)

def delete_chat(chat_id):
    file_path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
