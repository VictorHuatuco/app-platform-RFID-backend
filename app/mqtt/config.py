import os
from dotenv import load_dotenv

load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "30"))
MQTT_QOS = int(os.getenv("MQTT_QOS", "1"))
MQTT_CA_CERT = os.getenv("MQTT_CA_CERT", "certs/ca.crt")

# Prefijo de todos los tópicos de tu app
MQTT_APP_PREFIX = os.getenv("MQTT_APP_PREFIX", "APP/LOTO_RFID")
