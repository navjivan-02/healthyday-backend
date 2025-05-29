from datetime import datetime
import gspread
from google.cloud import firestore
from google.oauth2.service_account import Credentials
import gspread
from config import SHEET_14D_PROCESSED, FIRESTORE_COLLECTION_NEW, GOOGLE_CREDENTIALS_PATH


def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scope)
    return gspread.authorize(creds)


def update_user_statuses():
    today = datetime.today().date()

    # === Sheets setup ===
    client = get_gspread_client()
    sheet1 = client.open(SHEET_NAME).worksheet(SHEET_14D_PROCESSED)
    rows = sheet1.get_all_records()

    # === Firestore setup ===
    db = firestore.client()

    for idx, row in enumerate(rows, start=2):
        mobile = str(row.get("Mobile_Number"))
        start = datetime.strptime(row["14D_Start_Date"], "%m/%d/%Y").date()
        end = datetime.strptime(row["14D_End_Date"], "%m/%d/%Y").date()

        if start <= today <= end:
            new_status = "ongoing"
        elif today > end:
            new_status = "completed"
        else:
            continue  # future user or already updated

        # Google Sheets update
        sheet1.update_cell(idx, 8, new_status)  # Status column is column 8

        # Firestore update
        db.collection(FIRESTORE_COLLECTION_NEW).document(mobile).update({"Status": new_status})

if __name__ == "__main__":
    update_user_statuses()
