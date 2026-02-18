import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    data = response.json()
    print("Available Models Detail:")
    for model in data.get('models', []):
        print(f"- {model['name']} (Display: {model['displayName']})")
except Exception as e:
    print(f"Error: {e}")
