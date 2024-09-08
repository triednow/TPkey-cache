import os
import json
import time
import requests
from datetime import datetime

apikey = ""  # get your own API key from "https://babel-in.xyz"
cache_folder = "_cache_" # cacheFile
cache_time = 691200  # 8 days in seconds

if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

def fetch_and_cache_data():
    url = f"https://babel-in.xyz/{apikey}/tata/channels"
    headers = {'User-Agent': 'Babel-In'}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return
        if not response.content:
            print("Error: Received empty response")
            return

        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON response")
            return

        if data:
            for channel in data.get("data", []):
                channel_id = channel.get('id')
                channel_key = channel.get('channel_key')
                
                if isinstance(channel_key, dict):
                    keys = channel_key.get('keys', [])
                    if keys:
                        k = keys[0].get('k')
                        kid = keys[0].get('kid')
                        print(f"[key fetched for channel ID: {channel_id}]")
                    else:
                        k = None
                        kid = None
                        print(f"[No Key Found for channel ID: {channel_id}]")
                else:
                    keys = [] 
                    k = None
                    kid = None
                    print(f"[No Key Found for channel ID: {channel_id}]")

                cache_file = os.path.join(cache_folder, f"{channel_id}.json")

                if os.path.exists(cache_file):
                    with open(cache_file, 'r') as file:
                        existing_data = json.load(file)

                    key_exists = False
                    for value in existing_data:
                        for key in value.get('keys', []):
                            if key.get('k') == k and key.get('kid') == kid:
                                key_exists = True
                                print(f"[key already exists for channel ID: {channel_id}]")
                                break

                    if not key_exists:
                        new_data = []
                        current_time = datetime.now()

                        for value in existing_data:
                            time_added = datetime.strptime(value['time_added'], '%Y-%m-%d %H:%M:%S')
                            if (current_time - time_added).total_seconds() <= cache_time:
                                new_data.append(value)

                        new_data.append({
                            'keys': [{'kty': 'oct', 'k': k, 'kid': kid}] if keys else [],
                            'type': 'temporary',
                            'time_added': current_time.strftime('%Y-%m-%d %H:%M:%S')
                        })

                        with open(cache_file, 'w') as file:
                            json.dump(new_data, file, indent=4)
                else:
                    new_data = [{
                        'keys': [{'kty': 'oct', 'k': k, 'kid': kid}] if keys else [],
                        'type': 'temporary',
                        'time_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }]
                    with open(cache_file, 'w') as file:
                        json.dump(new_data, file, indent=4)
        else:
            print("Error: No data found in the response.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# Run the function infinitely every 9 minutes
while True:
    fetch_and_cache_data()
    print("Sleeping for 9 minutes...")
    time.sleep(9 * 60)  # Sleep for 9 minutes
