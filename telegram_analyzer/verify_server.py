import urllib.request
import json
import sys

def check_url(url, description):
    print(f"Checking {description} at {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            status = response.getcode()
            content = response.read().decode('utf-8')
            print(f"Status: {status}")
            print(f"Content length: {len(content)}")
            if status == 200:
                print("SUCCESS")
                return True, content
            else:
                print(f"FAILED with status {status}")
                return False, content
    except Exception as e:
        print(f"ERROR: {e}")
        return False, str(e)

def main():
    # Check Root
    success, content = check_url("http://127.0.0.1:8000/", "Root URL")
    if not success:
        sys.exit(1)
    
    if "<title>Telegram Intent Analyzer</title>" in content:
        print("Root page content verified.")
    else:
        print("Root page content MISMATCH.")
        sys.exit(1)

    # Check API Status
    success, content = check_url("http://127.0.0.1:8000/api/status", "API Status")
    if not success:
        sys.exit(1)
        
    try:
        data = json.loads(content)
        if "authorized" in data:
            print(f"API Verified. Auth Status: {data['authorized']}")
        else:
            print("API response malformed.")
            sys.exit(1)
    except json.JSONDecodeError:
        print("API response is not JSON.")
        sys.exit(1)

    print("\nALL CHECKS PASSED. Server is running correctly.")

if __name__ == "__main__":
    main()
