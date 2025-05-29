from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from utils.phone_utils import validate_mobile
from utils.source_utils import parse_source_and_ref
from integrations.google_sheets import save_to_sheets,create_shortio_link
from integrations.firestore_db import check_existing_user, save_to_firestore, get_active_users, write_to_14day_firestore
from integrations.google_sheets import write_to_14day_sheet, update_status, up
from integrations.firestore_db import mark_user_completed
from integrations.whatsapp_api import send_whatsapp_message
from datetime import datetime, timedelta, timezone
from config import API_SECRET_KEY, AISENSY_API_KEY


app = Flask(__name__)
CORS(app)


def check_auth(request):
    api_key = request.headers.get("X-API-Key")
    if api_key != API_SECRET_KEY:
        return False
    return True

def get_next_monday(start_date=None):
    if not start_date:
        start_date = datetime.now()
    days_ahead = (7 - start_date.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return start_date + timedelta(days=days_ahead)

def prepare_14day_data(mobile, name):
    now = datetime.now()
    reg_date = now.strftime('%m/%d/%Y')

    # Dates
    start_date = get_next_monday(now)
    end_date = start_date + timedelta(days=13)

    # Slug
    last_six = mobile[-6:]
    slug = f"{start_date.strftime('%d%m')}-{last_six}"
    short_link = f"https://startyoga.short.gy/{slug}"


    return {
        "Mobile_Number": mobile,
        "Name": name,
        "Slug": slug,
        "Reg_Date": reg_date,
        "14D_Start_Date": start_date.strftime('%m/%d/%Y'),
        "14D_End_Date": end_date.strftime('%m/%d/%Y'),
        "14D_Link": short_link
    }


@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        name = data.get("name")
        mobile = data.get("mobile")

        if not name or not mobile:
            return jsonify({"error": "Name and mobile are required"}), 400

        # Validate mobile number
        valid_mobile = validate_mobile(mobile)
        cleaned_mobile = ''.join(filter(str.isdigit, mobile))

        # Get referrer and source from query string
        referrer_mobile, source = parse_source_and_ref(request.args)

        # Check if already registered
        status = check_existing_user(valid_mobile)
        if status == "completed":
            return jsonify({"message": "You already completed the 14-day demo. Please subscribe to continue."})
        elif status == "active":
            return jsonify({"message": "You're already in the 14-day program. Please join with your existing link."})
        elif status == "queued":
            return jsonify({"message": "You’ve already registered. Your batch starts next Monday."})



        # Save to Firestore
        save_to_firestore(name, valid_mobile,referrer_mobile, source)

        # Save to Google Sheets
        save_to_sheets(
            name=name,
            mobile=cleaned_mobile,
            formatted_mobile=valid_mobile,
            source=source,
            referrer_mobile=referrer_mobile,
            existing="No",
            status="queued"
        )

        # Step: Prepare extra sheet data
        extra_sheet_data = prepare_14day_data(mobile, name)
        slug = extra_sheet_data["Slug"]
        start_date=extra_sheet_data["14D_Start_Date"]
        end_date=extra_sheet_data["14D_End_Date"]
        short_link = extra_sheet_data["14D_Link"]

        # Step: Write this to your second Google Sheet
        write_to_14day_sheet(extra_sheet_data)

        
        # Save to Firestore
        write_to_14day_firestore(extra_sheet_data)

        send_whatsapp_message(mobile,name,short_link) #Send welcome message after registration

        update_status(mobile=mobile, new_status="registered") #If everything is alright then registered status


        #Link generation
        response=create_shortio_link(slug, start_date, end_date)

        print("Short.io API response:", response)  # 🔍 Debug line



        return jsonify({
            "message": f"Registration successful for {name}",
            "mobile": valid_mobile,
            "source": source,
            "used_referrer_mobile": referrer_mobile
        })

    except Exception as e:
        import traceback
        traceback.print_exc()  # Shows the full error in terminal
        return jsonify({"error": str(e)}), 500


@app.route("/mark_completed", methods=["GET"])
def mark_completed():
    # Auth check
    api_key = request.headers.get("X-API-Key")
    if api_key != API_SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    active_users = get_active_users()
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=14)
    updated_count = 0

    for user in active_users:
        activated_date = datetime.fromisoformat(user["activated_at"]).replace(tzinfo=timezone.utc)
        if activated_date < cutoff_date:
            mark_user_completed(user["id"])
            updated_count += 1

    return jsonify({
        "message": f"Marked {updated_count} users as completed.",
        "count": updated_count
    })




if __name__ == "__main__":
    app.run(debug=True)

