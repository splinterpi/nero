#!/usr/bin/env python3
"""
Sense HAT → MQTT publisher with:
- All sensors: temp, humidity, pressure, orientation, compass, accelerometer, gyroscope
- Home Assistant MQTT discovery for all sensors
- Rolling logs with random jitter
- Single JSON payload OR multi-topic
- Dynamic CPU-based temperature correction
- OTA remote configuration reload (MQTT)
- Systemd-ready continuous loop
- MQTT Last Will & Testament (LWT) for online/offline status
"""

import paho.mqtt.client as mqtt
from sense_hat import SenseHat
import configparser
import json
import os
import time
import datetime
import signal
import logging
import random
from logging.handlers import RotatingFileHandler

CONFIG_FILE = "/etc/sensehat-mqtt.conf"
LOG_FILE = "/var/log/sensehat_mqtt.log"

# ------------------ Logging Setup ------------------
logger = logging.getLogger("sensehat")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# ------------------ Load Config ------------------
def load_config(path):
    parser = configparser.ConfigParser()
    parser.read(path)

    def get(section, key, default, cast=str):
        try:
            value = parser.get(section, key)
            if cast == bool:
                return value.lower() in ("1", "yes", "true", "on")
            return cast(value)
        except:
            return default

    return {
        "mqtt_host": get("mqtt", "host", "localhost"),
        "mqtt_port": get("mqtt", "port", 1883, int),
        "mqtt_username": get("mqtt", "username", None),
        "mqtt_password": get("mqtt", "password", None),
        "mqtt_client_id": get("mqtt", "client_id", "sensehat_publisher"),

        "single_payload": get("publish", "single_payload", True, bool),
        "state_topic": get("publish", "state_topic", "sensehat/sensor"),
        "publish_interval": get("publish", "publish_interval", 60, int),
        "jitter_max": get("publish", "jitter_max", 5, int),

        # Sensors
        "enable_temperature": get("sensors", "enable_temperature", True, bool),
        "enable_humidity": get("sensors", "enable_humidity", True, bool),
        "enable_pressure": get("sensors", "enable_pressure", True, bool),
        "enable_orientation": get("sensors", "enable_orientation", False, bool),
        "enable_compass": get("sensors", "enable_compass", False, bool),
        "enable_accelerometer": get("sensors", "enable_accelerometer", False, bool),
        "enable_gyroscope": get("sensors", "enable_gyroscope", False, bool),

        # Temperature correction
        "enable_temperature_correction": get("temperature", "enable_temperature_correction", False, bool),
        "temp_correction_factor": get("temperature", "temp_correction_factor", 0.8, float),

        # Home Assistant discovery
        "ha_discovery": get("discovery", "enabled", True, bool),
        "ha_prefix": get("discovery", "prefix", "homeassistant"),

        # OTA
        "enable_ota_reload": get("ota", "enable_ota_reload", True, bool),
        "ota_reload_topic": get("ota", "ota_reload_topic", "sensehat/config/reload"),
    }

config = load_config(CONFIG_FILE)
sense = SenseHat()
running = True

# ------------------ CPU Temperature ------------------
def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp","r") as f:
            return int(f.read()) / 1000.0
    except:
        return None

# ------------------ Read Sensors ------------------
def read_sensors():
    data = {}

    if config["enable_temperature"]:
        raw = sense.get_temperature()
        if config["enable_temperature_correction"]:
            cpu_t = get_cpu_temp()
            if cpu_t:
                raw = raw - (cpu_t - raw) * config["temp_correction_factor"]
        data["temperature"] = round(raw, 2)

    if config["enable_humidity"]:
        data["humidity"] = round(sense.get_humidity(), 2)

    if config["enable_pressure"]:
        data["pressure"] = round(sense.get_pressure(), 2)

    if config["enable_orientation"]:
        data["orientation"] = sense.get_orientation()

    if config["enable_compass"]:
        data["compass"] = sense.get_compass_raw()

    if config["enable_accelerometer"]:
        data["accelerometer"] = sense.get_accelerometer_raw()

    if config["enable_gyroscope"]:
        data["gyroscope"] = sense.get_gyroscope_raw()

    data["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    return data

# ------------------ Home Assistant Discovery ------------------
def ha_sensor_config(uid, name, device_class, unit, state_class, sensor_key):
    topic = (
        f"{config['state_topic']}/state"
        if config["single_payload"]
        else f"{config['state_topic']}/{sensor_key}"
    )
    payload = {
        "name": name,
        "unique_id": uid,
        "state_topic": topic,
        "device_class": device_class if device_class != "none" else None,
        "unit_of_measurement": unit if unit != "none" else None,
        "state_class": state_class,
        "value_template": f"{{{{ value_json.{sensor_key} }}}}",
        "device": {
            "identifiers": ["sensehat_001"],
            "manufacturer": "Raspberry Pi Foundation",
            "model": "Sense HAT",
            "name": "Sense HAT"
        }
    }
    # Remove None entries
    return {k:v for k,v in payload.items() if v is not None}

def publish_discovery(client):
    if not config["ha_discovery"]:
        return

    sensors = []
    if config["enable_temperature"]:
        sensors.append(("sensehat_temp","SenseHat Temperature","temperature","°C","measurement","temperature"))
    if config["enable_humidity"]:
        sensors.append(("sensehat_humidity","SenseHat Humidity","humidity","%","measurement","humidity"))
    if config["enable_pressure"]:
        sensors.append(("sensehat_pressure","SenseHat Pressure","pressure","hPa","measurement","pressure"))
    if config["enable_orientation"]:
        sensors.append(("sensehat_orientation","SenseHat Orientation","none","degrees","measurement","orientation"))
    if config["enable_compass"]:
        sensors.append(("sensehat_compass","SenseHat Compass","none","degrees","measurement","compass"))
    if config["enable_accelerometer"]:
        sensors.append(("sensehat_accelerometer","SenseHat Accelerometer","none","m/s²","measurement","accelerometer"))
    if config["enable_gyroscope"]:
        sensors.append(("sensehat_gyroscope","SenseHat Gyroscope","none","°/s","measurement","gyroscope"))

    for uid,name,device_class,unit,state_class,key in sensors:
        payload = ha_sensor_config(uid,name,device_class,unit,state_class,key)
        topic = f"{config['ha_prefix']}/sensor/{uid}/config"
        client.publish(topic,json.dumps(payload),retain=True)
        logger.info(f"HA discovery published: {topic}")

# ------------------ Publish Readings ------------------
def publish_readings(client):
    data = read_sensors()

    if config["single_payload"]:
        topic = f"{config['state_topic']}/state"
        client.publish(topic,json.dumps(data),retain=True)
        logger.info(f"Published single payload: {data}")
    else:
        for key,value in data.items():
            topic = f"{config['state_topic']}/{key}"
            client.publish(topic,json.dumps({"value":value}),retain=True)
            logger.info(f"Published {key}: {value}")

# ------------------ OTA Reload ------------------
def reload_config(client):
    global config
    logger.info("OTA reload requested...")
    new = load_config(CONFIG_FILE)
    config.update(new)
    logger.info("Config updated dynamically.")
    if config["ha_discovery"]:
        publish_discovery(client)

# ------------------ Graceful Shutdown ------------------
def handle_signal(sig, frame):
    global running
    logger.info("Received shutdown signal.")
    running = False

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# ------------------ Main ------------------
def main():
    client = mqtt.Client(client_id=config["mqtt_client_id"])

    # --- MQTT Last Will & Testament ---
    lwt_topic = "sensehat/status"
    lwt_payload = json.dumps({"status": "offline"})
    client.will_set(lwt_topic, payload=lwt_payload, qos=1, retain=True)

    if config["mqtt_username"]:
        client.username_pw_set(config["mqtt_username"], config["mqtt_password"])

    def on_connect(c, userdata, flags, rc):
        logger.info(f"MQTT connected rc={rc}")
        # Publish online status
        c.publish(lwt_topic, json.dumps({"status": "online"}), qos=1, retain=True)

        if config["enable_ota_reload"]:
            c.subscribe(config["ota_reload_topic"])
            logger.info(f"Subscribed to OTA topic: {config['ota_reload_topic']}")

    def on_message(c, userdata, msg):
        if config["enable_ota_reload"] and msg.topic == config["ota_reload_topic"]:
            if msg.payload.decode().strip().lower() == "reload":
                reload_config(c)

    client.on_connect = on_connect
    client.on_message = on_message

    logger.info(f"Connecting to MQTT broker ip={config["mqtt_host"]} port={config["mqtt_port"]}")
    client.connect(config["mqtt_host"],config["mqtt_port"],60)
    client.loop_start()
    publish_discovery(client)

    while running:
        publish_readings(client)
        sleep_sec = config["publish_interval"] + random.uniform(0, config["jitter_max"])
        time.sleep(sleep_sec)

    client.loop_stop()
    client.disconnect()
    logger.info("Service stopped cleanly.")

if __name__ == "__main__":
    main()

