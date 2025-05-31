import requests
from config import AISENSY_API_KEY, CAMPAIGN_NAME

def send_whatsapp_message(mobile, name, short_url):
    AISENSY_API_URL = "https://backend.aisensy.com/campaign/t1/api/v2"

    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": CAMPAIGN_NAME,
        "destination": f"91{mobile}",  # Ensure full number with country code
        "userName": name, 
        "templateParams": [short_url],  # Only `{{1}}` is used per your campaign
        "source": "new-landing-page form",
        "media": {
            "url": "https://whatsapp-media-library.s3.ap-south-1.amazonaws.com/IMAGE/6353da2e153a147b991dd812/4958901_highanglekidcheatingschooltestmin.jpg",
            "filename": "sample_media"
        },
        "buttons": [],
        "carouselCards": [],
        "location": {},
        "attributes": {
            "Pipeline": "14DWeek1",
            "JoiningLink": short_url
        },
        "paramsFallbackValue": {
            "FirstName": "user"
        }
    }

    try:
        response = requests.post(AISENSY_API_URL, json=payload)
        print(f"✅ WhatsApp sent to {mobile}: {response.status_code} - {response.text}")
        return response.status_code, response.text
    except Exception as e:
        print(f"❌ Error sending WhatsApp to {mobile}: {e}")
        return None, str(e)
