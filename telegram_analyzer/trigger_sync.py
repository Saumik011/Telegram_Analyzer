import urllib.request
import time

URL = "http://127.0.0.1:8000/api/chats/sync"

print("Triggering Chat Sync...")
try:
    req = urllib.request.Request(URL, method='POST')
    with urllib.request.urlopen(req) as response:
        print(f"Response: {response.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
