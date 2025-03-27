# get_last_5hrs_all_sensors.py

import boto3
import json
from datetime import datetime, timedelta

BUCKET_NAME = 'iot-weather-data-s3'
HOURS = 5

s3 = boto3.client('s3')

def list_objects():
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    return response.get('Contents', [])

def parse_timestamp(ts):
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

def filter_recent_data():
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=HOURS)
    result = []

    for obj in list_objects():
        try:
            file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            data = json.loads(file_obj['Body'].read())
            data_time = parse_timestamp(data['timestamp'])

            if data_time >= cutoff:
                result.append({
                    'station_id': data['station_id'],
                    'timestamp': data['timestamp'],
                    'temperature': data.get('temperature'),
                    'humidity': data.get('humidity'),
                    'co2': data.get('co2')
                })
        except Exception as e:
            print(f"Error reading {obj['Key']}: {e}")

    return result

def display_recent_sensor_values():
    print(f"\n Temperature, Humidity, and CO₂ data from the last {HOURS} hours:\n")
    results = filter_recent_data()
    
    for entry in results:
        print(f"{entry['timestamp']} | {entry['station_id']} | "
              f"Temp: {entry['temperature']} °C | "
              f"Humidity: {entry['humidity']} % | "
              f"CO₂: {entry['co2']} ppm")

if __name__ == "__main__":
    display_recent_sensor_values()
