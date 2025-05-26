import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

API_SECRET_KEY = os.getenv("API_SECRET_KEY")

GOOGLE_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials", "service_account.json")
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION")
AISENSY_API_KEY = os.getenv("AISENSY_API_KEY")
