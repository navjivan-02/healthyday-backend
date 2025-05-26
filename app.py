from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.phone_utils import validate_mobile
from utils.source_utils import parse_source_and_ref
from integrations.google_sheets import save_to_sheets
from integrations.firestore_db import check_existing_user, save_to_firestore, increment_referral, get_active_users
from integrations.google_sheets import increment_referral_count_in_sheets
from integrations.firestore_db import get_queued_users, mark_user_active, mark_user_completed
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


@app.route("/register", methods=["POST"])
def register():

    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        name = data.get("name")
        mobile = data.get("mobile")

        if not name or not mobile:
            return jsonify({"error": "Name and mobile are required"}), 400

        # Validate mobile number
        valid_mobile = validate_mobile(mobile)

        # Get referral and source from query string
        referrer_code, source = parse_source_and_ref(request.args)

        # Check if already registered
        status = check_existing_user(valid_mobile)
        if status == "completed":
            return jsonify({"message": "You already completed the 14-day demo. Please subscribe to continue."})
        elif status == "active":
            return jsonify({"message": "You're already in the 14-day program. Please join with your existing link."})
        elif status == "queued":
            return jsonify({"message": "You’ve already registered. Your batch starts next Monday."})

        # Generate referral code for this user
        import random, string
        user_referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Save to Firestore and Google Sheets
        save_to_firestore(name, valid_mobile, user_referral_code, referrer_code, source)
        save_to_sheets(name, valid_mobile, user_referral_code, referrer_code, source)

        # Increment referrer's count if valid
        if referrer_code:
            increment_referral(referrer_code)
            increment_referral_count_in_sheets(referrer_code)  # Sheets

        return jsonify({
            "message": f"Registration successful for {name}",
            "mobile": valid_mobile,
            "referral_code": user_referral_code,
            "source": source,
            "used_referral_code": referrer_code
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/send_reminders", methods=["GET"])
def send_reminders():
    # Auth check
    api_key = request.headers.get("X-API-Key")
    if api_key != API_SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    today = datetime.now().strftime("%A")  # E.g., 'Sunday'
    if today != "Sunday":
        return jsonify({"message": "Today is not Sunday. Reminders only go out one day before class."}), 200

    queued_users = get_queued_users()
    for user in queued_users:
        message = f"Hi {user['name']}, your 14-day Healthyday yoga class starts tomorrow! Please be ready to join on time."
        send_whatsapp_message(user["mobile"], message)
        mark_user_active(user["mobile"])

    return jsonify({
        "message": f"Sent reminders to {len(queued_users)} users.",
        "count": len(queued_users)
    })


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

