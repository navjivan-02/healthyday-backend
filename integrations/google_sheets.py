import gspread
from google.oauth2.service_account import Credentials
from config import SHEET_14D_NEW, SHEET_14D_PROCESSED, FIRESTORE_COLLECTION_NEW, SPREADSHEET_ID, GOOGLE_CREDENTIALS_PATH, SHORTIO_API_KEY
from datetime import datetime
from google.cloud import firestore
import requests
import os

def save_to_sheets(
    name,
    mobile,
    formatted_mobile,
    source,
    referrer_mobile,
    existing="No",
    status="queued"
):
    sheet = get_sheet(SHEET_14D_NEW)

    
    # Format date
    reg_date = datetime.now().strftime("%Y-%m-%d")
    
    row = [
        mobile,             # mobile_number
        name,               # Name
        existing,           # Existing
        source,             # Source
        reg_date,           # RegDate
        formatted_mobile,   # MobileNumberFormatted
        referrer_mobile,    # Referrer(Mob No)
        status              # Status
    ]
    
    sheet.append_row(row)


def get_sheet(sheet_name):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)

def write_to_14day_sheet(data):
    sheet = get_sheet(SHEET_14D_PROCESSED)

    # Prepare the row in correct column order
    row = [
        data["Mobile_Number"],
        data["Name"],
        data["Slug"],
        data["Reg_Date"],
        data["14D_Start_Date"],
        data["14D_End_Date"],
        data["14D_Link"]
    ]

    # Append the row to the sheet
    sheet.append_row(row)

def update_status(mobile, new_status):
    sheet = get_sheet(SHEET_14D_NEW)
    rows = sheet.get_all_records()

    def normalize_mobile(number):
        return ''.join(filter(str.isdigit, str(number)))

    target = normalize_mobile(mobile)
    updated = False

    for idx, row in enumerate(rows, start=2):
        sheet_number = normalize_mobile(row.get("MobileNumberFormatted", ""))
        if sheet_number == target:
            sheet.update_cell(idx, 8, new_status)
            print(f"[Sheet] Updated row {idx} for mobile {mobile}")
            updated = True
            break

    if not updated:
        print(f"[Sheet] Mobile {mobile} not found in sheet!")

    # Firestore update
    db = firestore.Client()
    db.collection(FIRESTORE_COLLECTION_NEW).document(mobile).update({"status": new_status})
    print(f"[Firestore] Updated status for {mobile} → {new_status}")

def create_shortio_link(slug, start_date, end_date):
    DOMAIN = "startyoga.short.gy"
    FOLDER_ID = "NN1xHJ41dNKtrerkWZPFd"
    ORIGINAL_URL = "https://www.instagram.com/healthydayyoga/"  # default instagram page


    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": SHORTIO_API_KEY
    }

    start_dt = datetime.strptime(start_date, "%m/%d/%Y")
    end_dt = datetime.strptime(end_date, "%m/%d/%Y")

    print("Start:", start_dt, "→", int(start_dt.timestamp()))
    print("End:", end_dt, "→", int(end_dt.timestamp()))


    body = {
        "domain": DOMAIN,
        "originalURL": ORIGINAL_URL,
        "path": slug,
        "expiresAt": int(end_dt.timestamp()*1000),
        "startDate": int(start_dt.timestamp()*1000),
        "folderId": FOLDER_ID
    }


    response = requests.post("https://api.short.io/links", json=body, headers=headers)

    try:
        data = response.json()
        if response.status_code == 201 or data.get("success"):
            print(f"✅ Link created: {data['shortURL']}")
            return data
        else:
            print(f"❌ Short.io error: {response.text}")
            return None
    except Exception as e:
        print("⚠️ JSON decode error:", e)
        return None