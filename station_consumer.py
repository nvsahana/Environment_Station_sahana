# station_consumer.py
from station import init_mqtt_connection
import time
import json
import argparse
import boto3
import uuid

# Initialize S3 client
s3 = boto3.client('s3')
BUCKET_NAME = 'iot-weather-data-s3'  # Replace with your actual bucket name

# MQTT callback to store incoming message in S3
def store_data(client, userdata, message):
    try:
        msg = message.payload.decode('utf8')
        print("Received MQTT message:", msg)
        data = json.loads(msg)

        # Only keep temperature, humidity, and CO2
        filtered_data = {
            'station_id': data['station_id'],
            'timestamp': data['timestamp'],
            'temperature': data.get('temperature'),
            'humidity': data.get('humidity'),
            'co2': data.get('co2')
        }

        # Create unique file name
        filename = f"{filtered_data['station_id']}_{filtered_data['timestamp'].replace(':', '-').replace(' ', '_')}_{uuid.uuid4()}.json"

        # Upload to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=json.dumps(filtered_data),
            ContentType='application/json'
        )

        print(f"Uploaded to S3 as: {filename}")

    except Exception as e:
        print(f"Error uploading to S3: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Init MQTT Consumer for AWS IoT + S3')
    parser.add_argument('--clientid', type=str, default='cons1')
    parser.add_argument('--topic', type=str, default='station')
    args = parser.parse_args()

    clientId = args.clientid
    topic = args.topic

    print("========== Running With ==========")
    print("ClientID:\t%s" % clientId)
    print("Topic:\t%s" % topic)

    mqtt_client = init_mqtt_connection(clientId=clientId)
    mqtt_client.connect()

    mqtt_client.subscribe(topic, 1, store_data)

    while True:
        print("Listening...")
        time.sleep(60)
