from flask import Flask, request, jsonify
import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("AD_ACCOUNT_ID")
PAGE_ID = os.getenv("PAGE_ID")
openai.api_key = OPENAI_API_KEY

@app.route('/create-ad', methods=['POST'])
def create_ad():
    data = request.json
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "Missing prompt"}), 400

    try:
        ad_text = generate_ad_text(prompt)
        image_url = generate_image(prompt)
        campaign_id, adset_id, ad_id = create_facebook_ad(ad_text, image_url)

        return jsonify({
            "status": "success",
            "campaign_id": campaign_id,
            "ad_id": ad_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_ad_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "אתה יועץ שיווק יצירתי."},
            {"role": "user", "content": f"כתוב טקסט שיווקי קצר לפייסבוק עבור: {prompt}"}
        ]
    )
    return response.choices[0].message.content.strip()

def generate_image(prompt):
    response = openai.Image.create(
        prompt=f"Create a visually appealing image for: {prompt}",
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']

def create_facebook_ad(ad_text, image_url):
    campaign_resp = requests.post(
        f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}/campaigns",
        params={"access_token": FACEBOOK_ACCESS_TOKEN},
        data={
            "name": "Auto Campaign",
            "objective": "LINK_CLICKS",
            "status": "PAUSED"
        }
    )
    campaign_id = campaign_resp.json().get("id")

    img_data = requests.get(image_url).content
    files = {'file': ('image.jpg', img_data)}
    image_resp = requests.post(
        f"https://graph.facebook.com/v19.0/act_{AD_ACCOUNT_ID}/adimages",
        params={"access_token": FACEBOOK_ACCESS_TOKEN},
        files=files
    )
    image_hash = list(image_resp.json()['images'].values())[0]['hash']

    creative_resp = requests.post(
        f"https://graph.facebook.com/v19.0/act_{AD_ACCOUNT_ID}/adcreatives",
        params={"access_token": FACEBOOK_ACCESS_TOKEN},
        json={
            "name": "Auto Creative",
            "object_story_spec": {
                "page_id": PAGE_ID,
                "link_data": {
                    "message": ad_text,
                    "link": "https://your-landing-page.com",
                    "image_hash": image_hash
                }
            }
        }
    )
    creative_id = creative_resp.json().get("id")

    adset_resp = requests.post(
        f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}/adsets",
        params={"access_token": FACEBOOK_ACCESS_TOKEN},
        data={
            "name": "Auto Ad Set",
            "campaign_id": campaign_id,
            "daily_budget": 1000,
            "billing_event": "IMPRESSIONS",
            "optimization_goal": "LINK_CLICKS",
            "targeting": '{"geo_locations":{"countries":["IL"]}}',
            "start_time": "2025-07-24T00:00:00-0700",
            "end_time": "2025-07-26T00:00:00-0700",
            "status": "PAUSED"
        }
    )
    adset_id = adset_resp.json().get("id")

    ad_resp = requests.post(
        f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}/ads",
        params={"access_token": FACEBOOK_ACCESS_TOKEN},
        data={
            "name": "Auto Ad",
            "adset_id": adset_id,
            "creative": f"{{\"creative_id\":\"{creative_id}\"}}",
            "status": "PAUSED"
        }
    )
    ad_id = ad_resp.json().get("id")

    return campaign_id, adset_id, ad_id

if __name__ == '__main__':
    app.run(debug=True)
