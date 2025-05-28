import requests

def create_shortio_link(slug, start_date, end_date):
    SHORTIO_API_KEY = "your-shortio-api-key"
    DOMAIN = "start.dailyyogawithjagan.com"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": SHORTIO_API_KEY
    }

    body = {
        "domain": DOMAIN,
        "originalURL": "https://dailyvideos.dailyyogawithjagan.com/placeholder",  # temp URL
        "path": slug,
        "expiresAt": f"{end_date}T23:59:59Z",
        "startDate": f"{start_date}T00:00:00Z"
    }

    response = requests.post("https://api.short.io/links", json=body, headers=headers)

    if response.status_code == 201:
        print(f"✅ Short.io link created for slug: {slug}")
    else:
        print(f"❌ Failed to create Short.io link: {response.text}")
