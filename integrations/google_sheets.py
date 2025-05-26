import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_CREDENTIALS_PATH, SPREADSHEET_ID, SHEET_NAME

def get_sheet():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

def save_to_sheets(name, mobile, referral_code, referrer_code, source):
    sheet = get_sheet()
    row = [name, mobile, referral_code, referrer_code, source, "queued"]
    sheet.append_row(row)

def get_all_referral_codes():
    """Returns a dict of referral_code → (row_index, row_data)"""
    sheet = get_sheet()
    records = sheet.get_all_values()
    codes = {}

    for i, row in enumerate(records[1:], start=2):  # Skip header row
        if len(row) >= 3:
            code = row[2].strip().upper()
            if code:
                codes[code] = (i, row)
    return codes


def increment_referral_count_in_sheets(referral_code):
    sheet = get_sheet()
    codes = get_all_referral_codes()

    if referral_code in codes:
        row_index, row = codes[referral_code]
        current_count = 0
        if len(row) >= 7:
            try:
                current_count = int(row[6])
            except ValueError:
                current_count = 0
        new_count = current_count + 1
        sheet.update_cell(row_index, 7, str(new_count))  # Column G = 7

def update_status_in_sheet(mobile, new_status):
    sheet = get_sheet()
    records = sheet.get_all_values()

    for i, row in enumerate(records[1:], start=2):  # Start from row 2
        if len(row) >= 2 and row[1].strip() == mobile:
            sheet.update_cell(i, 6, new_status)  # Column F = 6
            print(f"[Sheets] Status for {mobile} updated to {new_status}")
            return
    print(f"[Sheets] Mobile {mobile} not found in sheet.")

