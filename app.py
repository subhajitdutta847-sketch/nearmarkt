from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import os

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
sheet = client.open("NearMarkt_Search_Logs").sheet1

@app.route('/log-search', methods=['POST'])
def log_search():
    data = request.json

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    location = data.get('location', 'Unknown')
    product = data.get('product', 'Unknown')

    sheet.append_row([timestamp, location, product])

    return jsonify({"status": "success"})

@app.route('/')
def home():
    return "NearMarkt Backend Running"

if __name__ == '__main__':
    app.run(debug=True, port=5000)