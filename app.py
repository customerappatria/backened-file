import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID_USERS = os.environ.get('AIRTABLE_TABLE_ID_USERS')
AIRTABLE_TABLE_ID_DEVICES = os.environ.get('AIRTABLE_TABLE_ID_DEVICES')
AIRTABLE_API_URL_USERS = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID_USERS}'
AIRTABLE_API_URL_DEVICES = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID_DEVICES}'
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_TOKEN')

def fetch_linked_devices(device_ids):
    headers = {
        'Authorization': f'Bearer {AIRTABLE_TOKEN}',
        'Content-Type': 'application/json'
    }
    device_sns = []
    for device_id in device_ids:
        response = requests.get(f"{AIRTABLE_API_URL_DEVICES}/{device_id}", headers=headers)
        response.raise_for_status()
        device_record = response.json().get('fields', {})
        device_sns.append(device_record.get('Device Serial Number'))
    return device_sns

@app.route('/api/check_phone', methods=['POST'])
def check_phone():
    data = request.json
    phone_number = data.get('phoneNumber')
    
    headers = {
        'Authorization': f'Bearer {AIRTABLE_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Fetch user records
    response = requests.get(f"{AIRTABLE_API_URL_USERS}?filterByFormula={{Phone}}='{phone_number}'", headers=headers)
    response.raise_for_status()
    user_records = response.json().get('records', [])
    
    if not user_records:
        return jsonify({'status': 'error', 'message': 'Phone number not found'}), 404
    
    # Get user's name and device list
    user_record = user_records[0]['fields']
    user_name = user_record.get('Name')
    linked_device_ids = user_record.get('Device', [])
    
    if linked_device_ids:
        device_sns = fetch_linked_devices(linked_device_ids)
        return jsonify({'status': 'success', 'name': user_name, 'devices': device_sns, 'default_device': device_sns[0]})
    
    return jsonify({'status': 'error', 'message': 'No devices found for this phone number'}), 404

@app.route('/api/dashboard', methods=['POST'])
def dashboard_data():
    data = request.json
    device_sn = data.get('device_sn')
    date = data.get('date')
    view_mode = data.get('view_mode')
    month = data.get('month')
    year = data.get('year')
    
    if not device_sn:
        return jsonify({'error': 'Device serial number is required'}), 400

    result = main(device_sn, date, view_mode, month, year)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
