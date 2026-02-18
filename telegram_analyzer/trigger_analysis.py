import urllib.request
import time

CHAT_ID = "-1002063367336"
URL = f"http://127.0.0.1:8000/api/chats/{CHAT_ID}/analyze"

print(f"Triggering analysis for {CHAT_ID}...")
try:
    with urllib.request.urlopen(URL) as response:
        print(f"Response: {response.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
