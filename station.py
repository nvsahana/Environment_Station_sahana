# station.py
import random as r
import sys
import time
import json
import logging
import datetime
import argparse
import GLOBAL_PARAMS
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

def clip_value(minimum, maximum, value):
    return max(minimum, min(value, maximum))

def read_sensors():
    temperature = r.uniform(GLOBAL_PARAMS.TEMP_MIN, GLOBAL_PARAMS.TEMP_MAX)
    temperature += r.gauss(GLOBAL_PARAMS.NOISE_MEAN, GLOBAL_PARAMS.NOISE_STD)
    temperature = clip_value(GLOBAL_PARAMS.TEMP_MIN, GLOBAL_PARAMS.TEMP_MAX, temperature)

    humidity = r.gauss(GLOBAL_PARAMS.HUM_MEAN, GLOBAL_PARAMS.HUM_STD)
    humidity += r.gauss(GLOBAL_PARAMS.NOISE_MEAN, GLOBAL_PARAMS.NOISE_STD)
    humidity = clip_value(GLOBAL_PARAMS.HUM_MIN, GLOBAL_PARAMS.HUM_MAX, humidity)

    co2 = r.uniform(GLOBAL_PARAMS.CO2_MIN, GLOBAL_PARAMS.CO2_MAX)
    co2 += r.gauss(GLOBAL_PARAMS.NOISE_MEAN, GLOBAL_PARAMS.NOISE_STD)
    co2 = clip_value(GLOBAL_PARAMS.CO2_MIN, GLOBAL_PARAMS.CO2_MAX, co2)

    return temperature, humidity, co2

def init_mqtt_connection(useWebsocket=False,
    clientId='station1',
    host='a324iczif72eol-ats.iot.eu-north-1.amazonaws.com',
    rootCAPath='root_ca.pem',
    privateKeyPath='station.private.pem.key',
    certificatePath='station.pem.crt'):

    port = 8883 if not useWebsocket else 443

    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.NOTSET)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    if useWebsocket:
        mqtt_client = AWSIoTMQTTClient(clientId, useWebsocket=True)
        mqtt_client.configureEndpoint(host, port)
        mqtt_client.configureCredentials(rootCAPath)
    else:
        mqtt_client = AWSIoTMQTTClient(clientId)
        mqtt_client.configureEndpoint(host, port)
        mqtt_client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
    mqtt_client.configureOfflinePublishQueueing(-1)
    mqtt_client.configureDrainingFrequency(2)
    mqtt_client.configureConnectDisconnectTimeout(10)
    mqtt_client.configureMQTTOperationTimeout(5)

    return mqtt_client

def send_data(mqtt_client, data, topic):
    message = json.dumps(data)
    mqtt_client.publish(topic, message, 1)
    print('Published topic %s: %s\n' % (topic, message))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--clientid', type=str, default='station1')
    parser.add_argument('--topic', type=str, default='station')
    args = parser.parse_args()

    clientId = args.clientid
    topic = args.topic

    print("========== Running With ==========")
    print("ClientID:\t%s" % clientId)
    print("Topic:\t%s" % topic)

    mqtt_client = init_mqtt_connection(clientId=clientId)
    mqtt_client.connect()

    while True:
        temperature, humidity, co2 = read_sensors()
        data = {
            'station_id': clientId,
            'timestamp': datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': temperature,
            'humidity': humidity,
            'co2': co2
        }
        send_data(mqtt_client, data, topic)
        time.sleep(1)

    mqtt_client.disconnect()
