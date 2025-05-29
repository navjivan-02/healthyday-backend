import requests
from config import AISENSY_API_KEY, CAMPAIGN_NAME


def send_whatsapp_message(mobile, name, short_url):
    AISENSY_API_URL = "https://backend.aisensy.com/campaign/t1/api/v2"

    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": CAMPAIGN_NAME,
        "destination": mobile,
        "userName": name,
        "templateParams": [short_url],
        "attributes": {
            "Pipeline": "14DWeek1",
            "JoiningLink": short_url
        }
    }

    try:
        response = requests.post(AISENSY_API_URL, json=payload)
        print(f"✅ WhatsApp sent to {mobile}: {response.status_code} - {response.text}")
        return response.status_code, response.text
    except Exception as e:
        print(f"❌ Error sending WhatsApp to {mobile}: {e}")
        return None, str(e)
