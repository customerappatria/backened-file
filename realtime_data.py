import requests
import json
from datetime import datetime

AUTH_URL = 'https://lb.solinteg-cloud.com/openapi/v2/loginv2/auth'
AUTH_ACCOUNT = 'shailendra.nair@atriapower.com'
AUTH_PASSWORD = 'SolarEnergy'
BASE_DATA_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryDeviceRealtimeData'
DAY_AGGREGATE_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryDayAggregateValues'
MONTH_AGGREGATE_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryMonthAggregateValues'

def get_auth_token():
    payload = {
        'authAccount': AUTH_ACCOUNT,
        'authPassword': AUTH_PASSWORD
    }
    response = requests.post(AUTH_URL, json=payload)
    response.raise_for_status()
    auth_data = response.json()
    return auth_data['body']

def get_data(url, token, params):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'token': token
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_current_month_dates():
    now = datetime.now()
    start_date = now.strftime('%Y%m01')
    end_date = now.strftime('%Y%m%d')
    return start_date, end_date

def fetch_data(device_sn, token):
    start_date, end_date = get_current_month_dates()
    
    urls_and_params = [
        (BASE_DATA_URL, {'deviceSn': device_sn}),
        (DAY_AGGREGATE_URL, {'deviceSn': device_sn, 'date': end_date}),
        (MONTH_AGGREGATE_URL, {'deviceSn': device_sn, 'startDate': start_date, 'endDate': end_date})
    ]
    
    data_results = []
    for url, params in urls_and_params:
        data = get_data(url, token, params)
        data_results.append(data)
    return data_results

def main(device_sn):
    try:
        token = get_auth_token()
        realtime_data, day_aggregate_data, month_aggregate_data = fetch_data(device_sn, token)
        
        combined_data = {}
        
        if realtime_data and 'body' in realtime_data:
            combined_data.update(realtime_data['body'])
        else:
            return {'error': 'Failed to fetch realtime data.'}
        
        if day_aggregate_data and 'body' in day_aggregate_data:
            combined_data.update(day_aggregate_data['body'])
        else:
            return {'error': 'Failed to fetch day aggregate data.'}

        if month_aggregate_data and 'body' in month_aggregate_data:
            combined_data['productionThisMonth'] = month_aggregate_data['body'].get('pvGeneration', 'N/A')
        else:
            combined_data['productionThisMonth'] = 'N/A'

        return combined_data
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        return {'error': str(e)}

if __name__ == "__main__":
    pass
