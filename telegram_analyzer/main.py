import uvicorn
import os
import sys

# Define base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    print(f"Starting Telegram Analyzer from {BASE_DIR}")
    # Run the FastAPI app
    # We use string import to enable reload support if needed, though programmatic run is fine too
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True, app_dir=BASE_DIR)
