import os
from dotenv import load_dotenv

# Determine which .env file to load
env = os.getenv("ENV", "development")

if env == "production":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env.dev")
    


# Load common configs
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
DEFAULT_YOUTUBE_LINK = os.getenv("DEFAULT_YOUTUBE_LINK")

GOOGLE_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials", "service_account.json")
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION")
AISENSY_API_KEY = os.getenv("AISENSY_API_KEY")

print(f"[ENV] Loaded environment: {env}")
print(f"[CONFIG] API_SECRET_KEY = {API_SECRET_KEY}")
print(f"[CONFIG] DEFAULT_YOUTUBE_LINK = {DEFAULT_YOUTUBE_LINK}")