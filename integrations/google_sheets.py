import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_CREDENTIALS_PATH, SPREADSHEET_ID, SHEET_NAME
from datetime import datetime

def save_to_sheets(
    name,
    mobile,
    formatted_mobile,
    source,
    referrer_mobile,
    existing="No",
    status="queued"
):
    sheet = get_sheet("Sheet1")
    
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


def update_status_in_sheet(mobile, new_status):
    sheet = get_sheet("Sheet1")
    records = sheet.get_all_values()

    for i, row in enumerate(records[1:], start=2):  # Start from row 2
        if len(row) >= 2 and row[1].strip() == mobile:
            sheet.update_cell(i, 6, new_status)  # Column F = 6
            print(f"[Sheets] Status for {mobile} updated to {new_status}")
            return
    print(f"[Sheets] Mobile {mobile} not found in sheet.")

def write_to_14day_sheet(data):
    sheet = get_sheet("14D_processed")

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
