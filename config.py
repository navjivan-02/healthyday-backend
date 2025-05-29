import os
from dotenv import load_dotenv

# Determine which .env file to load
env = os.getenv("ENV", "development")
if env == "production":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env.dev")

# === API KEYS & SECRETS ===
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
DEFAULT_LINK = os.getenv("DEFAULT_LINK")
AISENSY_API_KEY = os.getenv("AISENSY_API_KEY")
SHORTIO_API_KEY = os.getenv("SHORTIO_API_KEY")

# === GOOGLE SHEET CONFIG ===
GOOGLE_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials", "service_account.json")
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")  # One spreadsheet ID for all tabs

SHEET_14D_NEW = "14D_new"
SHEET_14D_PROCESSED = "14D_processed"

# === FIRESTORE COLLECTIONS ===
FIRESTORE_COLLECTION_NEW = "registration_dev"
FIRESTORE_COLLECTION_PROCESSED = "14D_processed_dev"

# === DEBUG PRINTS ===
print(f"[ENV] Loaded environment: {env}")
print(f"[CONFIG] API_SECRET_KEY = {API_SECRET_KEY}")
print(f"[CONFIG] SHEET_ID = {SPREADSHEET_ID}")

# === WHATSAPP API ===
CAMPAIGN_NAME = "joining_link_v3"