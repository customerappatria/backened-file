import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from realtime_data import main

app = Flask(__name__)
CORS(app)

AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID =  os.environ.get('AIRTABLE_TABLE_ID')
AIRTABLE_API_URL = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_TOKEN')

@app.route('/api/check_phone', methods=['POST'])
def check_phone():
    data = request.json
    phone_number = data.get('phoneNumber')
    
    headers = {
        'Authorization': f'Bearer {AIRTABLE_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.get(AIRTABLE_API_URL, headers=headers)
    response.raise_for_status()
    records = response.json().get('records', [])
    
    for record in records:
        if record['fields'].get('Phone') == phone_number:
            return jsonify({'status': 'success', 'device_sn': record['fields'].get('Device')})
    
    return jsonify({'status': 'error', 'message': 'Phone number not found'}), 404

@app.route('/api/dashboard', methods=['POST'])
def dashboard_data():
    data = request.json
    device_sn = data.get('device_sn')
    if not device_sn:
        return jsonify({'error': 'Device serial number is required'}), 400

    result = main(device_sn)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
