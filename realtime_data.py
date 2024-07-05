import os
import requests
import json
from datetime import datetime

AUTH_URL = 'https://lb.solinteg-cloud.com/openapi/v2/loginv2/auth'
AUTH_ACCOUNT = os.environ.get('AUTH_ACCOUNT')
AUTH_PASSWORD = os.environ.get('AUTH_PASSWORD')
BASE_DATA_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryDeviceRealtimeData'
DAY_AGGREGATE_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryDayAggregateValues'
MONTH_AGGREGATE_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryMonthAggregateValues'
PRODUCTION_DAY_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryProductionDay'
MONTH_PRODUCTION_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryProductionMonth'
YEAR_PRODUCTION_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryProductionYear'

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

def fetch_production_day_data(device_sn, date, token):
    params = {'deviceSn': device_sn, 'date': date}
    data = get_data(PRODUCTION_DAY_URL, token, params)
    return data

def fetch_production_month_data(device_sn, month, token):
    start_date = month + '01'
    end_date = month + '31'
    params = {'deviceSn': device_sn, 'startDate': start_date, 'endDate': end_date}
    data = get_data(MONTH_PRODUCTION_URL, token, params)
    return data

def fetch_production_year_data(device_sn, year, token):
    start_date = year + '0101'
    end_date = year + '1231'
    params = {'deviceSn': device_sn, 'startDate': start_date, 'endDate': end_date}
    data = get_data(YEAR_PRODUCTION_URL, token, params)
    return data

def fetch_data(device_sn, token, date):
    start_date, end_date = get_current_month_dates()
    
    urls_and_params = [
        (BASE_DATA_URL, {'deviceSn': device_sn}),
        (DAY_AGGREGATE_URL, {'deviceSn': device_sn, 'date': end_date}),
        (MONTH_AGGREGATE_URL, {'deviceSn': device_sn, 'startDate': start_date, 'endDate': end_date}),
        (PRODUCTION_DAY_URL, {'deviceSn': device_sn, 'date': date})  # New URL for production day data
    ]
    
    data_results = []
    for url, params in urls_and_params:
        data = get_data(url, token, params)
        data_results.append(data)
    return data_results

def main(device_sn, date, view_mode=None, month=None, year=None):
    try:
        token = get_auth_token()
        data_results = fetch_data(device_sn, token, date)
        
        combined_data = {}
        
        realtime_data, day_aggregate_data, month_aggregate_data, production_day_data = data_results
        
        if realtime_data and 'body' in realtime_data:
            combined_data.update(realtime_data['body'])
        else:
            combined_data['realtime_data_error'] = 'Failed to fetch realtime data.'

        if day_aggregate_data and 'body' in day_aggregate_data:
            combined_data.update(day_aggregate_data['body'])
        else:
            combined_data['day_aggregate_data_error'] = 'Failed to fetch day aggregate data.'

        if month_aggregate_data and 'body' in month_aggregate_data:
            combined_data['productionThisMonth'] = month_aggregate_data['body'].get('pvGeneration', 'N/A')
        else:
            combined_data['productionThisMonth'] = 'N/A'

        if production_day_data and 'body' in production_day_data:
            combined_data['productionDay'] = production_day_data['body']
        else:
            combined_data['productionDay'] = []
        
        if view_mode == 'month' and month:
            production_month_data = fetch_production_month_data(device_sn, month, token)
            if production_month_data and 'body' in production_month_data:
                combined_data['productionMonth'] = production_month_data['body']
            else:
                combined_data['productionMonth'] = []
        
        if view_mode == 'year' and year:
            production_year_data = fetch_production_year_data(device_sn, year, token)
            if production_year_data and 'body' in production_year_data:
                combined_data['productionYear'] = production_year_data['body']
            else:
                combined_data['productionYear'] = []
        
        return combined_data
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        return {'error': str(e)}

if __name__ == "__main__":
    pass
