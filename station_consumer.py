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

        # Create unique file name
        filename = f"{data['station_id']}_{data['timestamp'].replace(':', '-').replace(' ', '_')}_{uuid.uuid4()}.json"

        # Upload to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=json.dumps(data),
            ContentType='application/json'
        )

        print(f"Uploaded to S3 as: {filename}")

    except Exception as e:
        print(f"Error uploading to S3: {e}")

if __name__ == "__main__":
    clientId = 'cons1'
    topic = 'station'

    parser = argparse.ArgumentParser(description='Init MQTT Consumer for AWS IoT + S3')
    parser.add_argument('--clientid', type=str, default='cons1')
    parser.add_argument('--topic', type=str, default='station')
    args = parser.parse_args()

    print("========== Running With ==========\nClientID:\t%s\nTopic:\t%s" % (args.clientid, args.topic))
    clientId = args.clientid
    topic = args.topic

    # Connect to AWS IoT
    myAWSIoTMQTTClient = init_mqtt_connection(clientId=clientId)
    myAWSIoTMQTTClient.connect()

    # Subscribe to the topic
    myAWSIoTMQTTClient.subscribe(topic, 1, store_data)

    while True:
        print("Listening...")
        time.sleep(60)
