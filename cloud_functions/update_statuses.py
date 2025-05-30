from datetime import datetime
import gspread
from google.cloud import firestore
from google.oauth2.service_account import Credentials
from config import SHEET_14D_PROCESSED, FIRESTORE_COLLECTION_NEW, GOOGLE_CREDENTIALS_PATH, SPREADSHEET_ID

def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scope)
    return gspread.authorize(creds)

def update_user_statuses():
    today = datetime.today().date()

    # === Setup ===
    db = firestore.Client()
    gclient = get_gspread_client()
    sheet = gclient.open_by_key(SPREADSHEET_ID).worksheet(SHEET_14D_PROCESSED)
    sheet_data = sheet.get_all_records()
    
    # Build lookup for row indexing in Sheets
    row_index_map = {str(row["Mobile_Number"]): idx+2 for idx, row in enumerate(sheet_data)}

    # === Process Firestore documents ===
    users_ref = db.collection(FIRESTORE_COLLECTION_NEW)
    users = users_ref.stream()

    for doc in users:
        data = doc.to_dict()
        mobile = str(data.get("Mobile_Number"))
        start_str = data.get("14D_Start_Date")
        end_str = data.get("14D_End_Date")

        if not (start_str and end_str):
            continue

        start_date = datetime.strptime(start_str, "%m/%d/%Y").date()
        end_date = datetime.strptime(end_str, "%m/%d/%Y").date()

        if start_date <= today <= end_date:
            status = "ongoing"
        elif today > end_date:
            status = "completed"
        else:
            continue  # not yet started

        # Update Firestore
        users_ref.document(mobile).update({"Status": status})

        # Update Google Sheet (only if row exists)
        if mobile in row_index_map:
            sheet.update_cell(row_index_map[mobile], 8, status)  # Column 8 is 'Status'

if __name__ == "__main__":
    update_user_statuses()
