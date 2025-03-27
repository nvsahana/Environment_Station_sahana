# Cloud-Based IoT Weather Station Simulation

This project simulates a virtual IoT-based environmental station that collects temperature, humidity, and CO2 data and sends it to the cloud via MQTT using AWS IoT Core. The data is stored in AWS S3 and can be queried for both real-time and historical insights.

---

## Features

- Simulates temperature (-50°C to 50°C), humidity (0–100%), and CO2 (300–2000 ppm)
- Publishes data via MQTT to AWS IoT Core
- Stores incoming data in an S3 bucket in JSON format
- Includes tools to:
  - Fetch the latest sensor reading
  - Query data from the past 5 hours
  - Handle data for multiple stations

---

## Project Structure

```
.
├── station.py                      # Virtual station - generates and publishes sensor data
├── station_consumer.py            # Subscribes to topic and stores data in S3
├── global_params.py               # Configuration for sensor ranges and distributions
├── last_data.py                   # Fetches latest reading from S3
├── get_last_5hrs_all_sensors.py   # Fetches past 5 hours of temp, humidity, CO2
├── requirements.txt               # Python dependencies
├── root_ca.pem                    # AWS IoT Core root CA cert
├── station.pem.crt                # AWS IoT Core device certificate
├── station.private.pem.key        # AWS IoT Core private key
```

---

## How to Run

Make sure you have AWS credentials set up and your certificates downloaded from AWS IoT Core.

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the simulated station (Publisher)
```bash
python station.py --clientid station1 --topic station
```

### 3. Start the consumer (Subscriber + S3 uploader)
```bash
python station_consumer.py --clientid cons1 --topic station
```

### 4. View the latest sensor reading
```bash
python last_data.py
```

### 5. View data from the last 5 hours
```bash
python get_last_5hrs_all_sensors.py
```

---

## AWS Configuration

- **IoT Core**: Register a device, generate and download keys/certs, attach a policy that allows MQTT publish/subscribe.
- **S3 Bucket**: Create a bucket (e.g., `iot-weather-data-s3`) with appropriate permissions.

---




