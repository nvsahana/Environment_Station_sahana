import boto3
import json
from datetime import datetime

BUCKET_NAME = 'iot-weather-data-s3'
STATION_ID = 'station1'

s3 = boto3.client('s3')

def list_objects():
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    return response.get('Contents', [])

def get_latest_file(objects):
    # Filter by station ID
    station_files = [obj for obj in objects if obj['Key'].startswith(STATION_ID)]
    # Sort by LastModified (most recent first)
    sorted_files = sorted(station_files, key=lambda x: x['LastModified'], reverse=True)
    return sorted_files[0] if sorted_files else None

def display_latest_data():
    objects = list_objects()
    latest_file = get_latest_file(objects)
    
    if not latest_file:
        print("No data found.")
        return

    obj = s3.get_object(Bucket=BUCKET_NAME, Key=latest_file['Key'])
    data = json.loads(obj['Body'].read())
    
    print(f"\nLatest data for {STATION_ID}:\n")
    for key, value in data.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    display_latest_data()
