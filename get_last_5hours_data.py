import boto3
import json
from datetime import datetime, timedelta

BUCKET_NAME = 'iot-weather-data-s3'
SENSOR_KEY = 'temperature'  # Change to humidity, rain_height, etc.
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
        file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=obj['Key'])
        try:
            data = json.loads(file_obj['Body'].read())
            data_time = parse_timestamp(data['timestamp'])

            if data_time >= cutoff:
                result.append({
                    'station_id': data['station_id'],
                    'timestamp': data['timestamp'],
                    SENSOR_KEY: data.get(SENSOR_KEY, None)
                })

        except Exception as e:
            print(f"Error reading {obj['Key']}: {e}")

    return result

def display_recent_sensor_values():
    print(f"\n📈 {SENSOR_KEY.capitalize()} data from the last {HOURS} hours:\n")
    results = filter_recent_data()
    
    for entry in results:
        print(f"{entry['timestamp']} | {entry['station_id']} | {SENSOR_KEY}: {entry[SENSOR_KEY]}")

if __name__ == "__main__":
    display_recent_sensor_values()
