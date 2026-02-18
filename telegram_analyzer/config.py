import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

class Config:
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    PHONE_NUMBER = os.getenv("PHONE_NUMBER")
    SESSION_NAME = os.getenv("SESSION_NAME", "anon_session")
    DB_PATH = os.getenv("DB_PATH", "telegram_analysis.db")
    
    # Analysis Configuration
    URGENCY_THRESHOLD = 70
    ENGAGEMENT_THRESHOLD = 50

    @staticmethod
    def validate():
        if not Config.API_ID or not Config.API_HASH:
            raise ValueError("API_ID and API_HASH must be set in environment variables or .env file.")

# Create a sample .env file if it doesn't exist
if not os.path.exists(".env"):
    with open(".env", "w") as f:
        f.write("API_ID=\nAPI_HASH=\nPHONE_NUMBER=\n")
