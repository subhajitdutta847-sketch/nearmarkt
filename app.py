#test2
from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
import requests

app = Flask(__name__)
CORS(app)

# Google Sheets setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Read credentials from environment variable on Render
# or from file locally
if os.environ.get('GOOGLE_CREDENTIALS'):
    creds_dict = json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

client = gspread.authorize(creds)

def get_local_timestamp():
    """Returns current time in Hamburg (Europe/Berlin), auto-adjusts for CET/CEST."""
    return datetime.now(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%d %H:%M:%S")

def get_place_name(lat, lng):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
        headers = {'User-Agent': 'NearMarkt/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        address = data.get('address', {})
        city = address.get('city') or address.get('town') or address.get('village') or 'Unknown'
        country = address.get('country', '')
        return f"{city}, {country}"
    except:
        return f"{lat}, {lng}"
sheet = client.open("NearMarkt_Search_Logs").sheet1

@app.route('/log-search', methods=['POST'])
def log_search():
    data = request.json

    timestamp = get_local_timestamp()
    location = data.get('location', 'Unknown')
    product = data.get('product', 'Unknown')
    email = data.get('email', 'Unknown')

    sheet.append_row([timestamp, location, product, email])

    return jsonify({"status": "success"})

@app.route('/')
def home():
    return "NearMarkt Backend Running"

@app.route('/check-password', methods=['POST'])
def check_password():
    data = request.json
    entered = data.get('password', '')
    correct = os.environ.get('BETA_PASSWORD', 'nearmarkt2024')
    
    if entered == correct:
        return jsonify({"status": "success", "token": "nm_beta_access_granted"})
    else:
        return jsonify({"status": "error", "message": "Wrong password"}), 401

@app.route('/beta-signup', methods=['POST'])
def beta_signup():
    data = request.json
    
    timestamp = get_local_timestamp()
    
    name = data.get('name', 'Unknown')
    email = data.get('email', 'Unknown')
    location_raw = data.get('location', 'Unknown')
    if ',' in str(location_raw):
        parts = location_raw.split(',')
        try:
            lat = float(parts[0])
            lng = float(parts[1])
            place = get_place_name(lat, lng)
            city = place.split(',')[0].strip()
            country = place.split(',')[1].strip() if ',' in place else 'Unknown'
        except:
            city = 'Unknown'
            country = 'Unknown'
    else:
        city = 'Unknown'
        country = 'Unknown'
    device = data.get('device', 'Unknown')
    browser = data.get('browser', 'Unknown')
    language = data.get('language', 'Unknown')
    
    # Open Beta Users sheet
    beta_sheet = client.open("NearMarkt_Search_Logs").worksheet("Beta Users")
    beta_sheet.append_row([
        timestamp,
        name,
        email,
        country,
        city,
        device,
        browser,
        language,
        "Pending"
    ])
    
    return jsonify({"status": "success"})
if __name__ == '__main__':
    app.run(debug=True, port=5000)