from google.cloud import firestore
from config import GOOGLE_CREDENTIALS_PATH, FIRESTORE_COLLECTION
from datetime import datetime, timedelta, timezone
from integrations.google_sheets import update_status_in_sheet
import os
import json

# Set GOOGLE_APPLICATION_CREDENTIALS env for Firestore SDK
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_PATH

db = firestore.Client()
collection = db.collection(FIRESTORE_COLLECTION)

def check_existing_user(mobile):
    """Check if the user exists and return their status."""
    doc = collection.document(mobile).get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("status", "unknown")
    return None

def save_to_firestore(name, mobile, referral_code, referrer_code, source):
    """Save a new registration record to Firestore."""
    data = {
        "name": name,
        "mobile": mobile,
        "referral_code": referral_code,
        "referrer_code": referrer_code,
        "source": source,
        "status": "queued",  # default status
    }
    collection.document(mobile).set(data)

def increment_referral(referrer_code):
    """Increment referral count for a user by their referral code."""
    query = collection.where("referral_code", "==", referrer_code).limit(1).stream()
    for doc in query:
        user_data = doc.to_dict()
        count = user_data.get("referral_count", 0)
        doc.reference.update({"referral_count": count + 1})


def get_queued_users():
    """Fetch all users whose status is 'queued'."""
    users = []
    docs = collection.where("status", "==", "queued").stream()
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id  # Store mobile as ID
        users.append(data)
    return users

def mark_user_active(mobile):
    collection.document(mobile).update({
        "status": "active",
        "activated_at": datetime.now(timezone.utc).isoformat()
    })
    update_status_in_sheet(mobile, "active")


def get_active_users():
    """Fetch all users with status 'active' and a valid activated_at date."""
    users = []
    docs = collection.where("status", "==", "active").stream()
    for doc in docs:
        data = doc.to_dict()
        if "activated_at" in data:
            data["id"] = doc.id  # Save mobile number
            users.append(data)
    return users

def mark_user_completed(mobile):
    collection.document(mobile).update({
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat()
    })
    update_status_in_sheet(mobile, "completed")
