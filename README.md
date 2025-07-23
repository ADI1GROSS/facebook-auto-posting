# Facebook Ad Generator API

This is a simple Flask-based API that:
- Accepts a text prompt
- Generates ad copy with OpenAI's GPT
- Creates a matching image using DALL·E
- Uploads the result to Facebook Ads using Meta's Marketing API

## 📦 Requirements
- Python 3.8+
- OpenAI API Key
- Facebook Marketing API Access Token
- Active Ad Account & Page ID

## 🧪 Running locally
```bash
pip install -r requirements.txt
python app.py
```

Send a POST request to:
```
http://localhost:5000/create-ad
{
  "prompt": "סדנת בישול טבעונית בתל אביב"
}
```

## 🚀 Deployment
Can be easily deployed on [Render](https://render.com) or with Docker:

### Docker
```bash
docker build -t facebook-ad-api .
docker run -p 5000:5000 --env-file .env facebook-ad-api
```

## 📁 .env file
```
OPENAI_API_KEY=your-key
FACEBOOK_ACCESS_TOKEN=your-token
AD_ACCOUNT_ID=act_1234567890
PAGE_ID=1234567890
```

## ⚠️ Note
This is an MVP demo – use responsibly and secure your keys.
