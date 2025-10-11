import os
import ssl
import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# -------------------------
# Cargar variables .env
# -------------------------
load_dotenv()
MQTT_HOST = os.getenv("MQTT_SIM_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_SIM_PORT", 1883))
MQTT_USER = os.getenv("MQTT_SIM_USER", "")
MQTT_PASSWORD = os.getenv("MQTT_SIM_PASSWORD", "")
MQTT_KEEPALIVE = int(os.getenv("MQTT_SIM_KEEPALIVE", 30))
MQTT_QOS = int(os.getenv("MQTT_SIM_QOS", 1))
MQTT_PREFIX = os.getenv("MQTT_SIM_PREFIX", "APP/LOTO_RFID")
MQTT_CA_CERT = os.getenv("MQTT_SIM_CA_CERT", "")
MODULE_CODE = "LOTO-RFID-V1-A01"

# -------------------------
# Topics
# -------------------------
TOPIC_TAGS = f"{MQTT_PREFIX}/{MODULE_CODE}/TAGS"
TOPIC_ONLINE = f"{MQTT_PREFIX}/{MODULE_CODE}/ONLINE"
TOPIC_LWT = f"{MQTT_PREFIX}/{MODULE_CODE}/LWT"
TOPIC_STATUS = f"{MQTT_PREFIX}/{MODULE_CODE}/STATUS"
TOPIC_USERS = f"{MQTT_PREFIX}/{MODULE_CODE}/USERS"

# -------------------------
# Datos simulados
# -------------------------
USERS = [
    {"name": "Victor Huatuco", "CARD": "192002151005100001", "LOTO": "192002151005200001"},
    {"name": "Pamela Matías", "CARD": "192002151005100002", "LOTO": "192002151005200002"},
    {"name": "María García", "CARD": "192002151005100003", "LOTO": "192002151005200003"},
]

# -------------------------
# MQTT EVENTOS
# -------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado al broker MQTT (SIMULADOR)")
        # Suscribirse a los tópicos de respuesta del backend
        client.subscribe([(TOPIC_STATUS, MQTT_QOS), (TOPIC_USERS, MQTT_QOS)])
        print(f"📡 Suscrito a: {TOPIC_STATUS} y {TOPIC_USERS}")
    else:
        print(f"❌ Error al conectar: rc={rc}")


def on_message(client, userdata, msg):
    """Muestra las respuestas del backend."""
    try:
        payload = json.loads(msg.payload.decode())
        if TOPIC_STATUS in msg.topic:
            print(f"💬 [STATUS] → {json.dumps(payload, indent=2)}")
        elif TOPIC_USERS in msg.topic:
            print(f"👥 [USERS] → {json.dumps(payload, indent=2)}")
        else:
            print(f"📩 [{msg.topic}] → {payload}")
    except Exception as e:
        print(f"⚠️ Error procesando mensaje MQTT: {e}")


# -------------------------
# FUNCIONES DE SIMULACIÓN
# -------------------------
def publish_json(client, topic, data):
    client.publish(topic, json.dumps(data), qos=MQTT_QOS)
    print(f"📤 [{topic}] → {json.dumps(data)}")


def send_online(client):
    payload = {"module_loto_code": MODULE_CODE, "status": "ONLINE"}
    publish_json(client, TOPIC_ONLINE, payload)


def send_lwt(client):
    payload = "offline"
    client.publish(TOPIC_LWT, payload, qos=MQTT_QOS)
    print("🔌 LWT enviado (desconectado)")


def send_tags(client, cards, lotos):
    payload = {
        "module_loto_code": MODULE_CODE,
        "tags": {
            "CARD": [
                {"tag_code": code, "timestamp": datetime.utcnow().isoformat() + "Z"}
                for code in cards
            ],
            "LOTO": [
                {"tag_code": code, "timestamp": datetime.utcnow().isoformat() + "Z"}
                for code in lotos
            ],
        },
    }
    publish_json(client, TOPIC_TAGS, payload)


# -------------------------
# ESCENARIOS
# -------------------------
def scenario_alert(client, user=None):
    """Usuario entra sin candado → genera alerta"""
    if not user:
        user = random.choice(USERS)
    print(f"\n🚨 [ESCENARIO ALERTA] {user['name']} entra SIN candado")
    send_tags(client, cards=[user["CARD"]], lotos=[])
    time.sleep(random.randint(4, 6))


def scenario_ok(client, user=None):
    """Usuario entra con su candado → todo ok"""
    if not user:
        user = random.choice(USERS)
    print(f"\n✅ [ESCENARIO OK] {user['name']} coloca su candado correctamente")
    send_tags(client, cards=[user["CARD"]], lotos=[user["LOTO"]])
    time.sleep(random.randint(4, 8))


def scenario_mantenimiento(client, user=None):
    """Simula un ciclo completo de mantenimiento"""
    if not user:
        user = random.choice(USERS)
    print(f"\n🛠️ [ESCENARIO MANTENIMIENTO] {user['name']} entra sin candado y luego coloca uno")
    send_tags(client, cards=[user["CARD"]], lotos=[])
    time.sleep(3)
    send_tags(client, cards=[user["CARD"]], lotos=[user["LOTO"]])
    time.sleep(random.randint(5, 8))
    send_tags(client, cards=[user["CARD"]], lotos=[])
    print(f"🔚 {user['name']} terminó su mantenimiento")
    time.sleep(3)


def scenario_idle(client, user=None):
    """Bahía sin actividad"""
    print("\n🌙 [ESCENARIO INACTIVO] Bahía sin trabajadores detectados")
    send_tags(client, cards=[], lotos=[])
    time.sleep(random.randint(6, 10))


# -------------------------
# SIMULACIÓN COMPLETA
# -------------------------
def simulate_realistic(client, total_cycles=6):
    send_online(client)
    time.sleep(3)

    scenarios = [scenario_alert, scenario_ok, scenario_mantenimiento, scenario_idle]

    for i in range(1, total_cycles + 1):
        print(f"\n🔁 --- CICLO {i}/{total_cycles} ---")
        scenario = random.choice(scenarios)
        user = random.choice(USERS)
        # Todas las funciones ahora aceptan user (aunque algunas no lo usen)
        scenario(client, user)
        time.sleep(random.randint(4, 8))

    send_lwt(client)
    print("\n🛑 Simulación finalizada.")



# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    client = mqtt.Client(client_id="loto-simulator", clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message

    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD or None)

    if MQTT_CA_CERT:
        client.tls_set(
            ca_certs=MQTT_CA_CERT,
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
        )
        print("🔒 TLS habilitado")

    print(f"🔗 Conectando al broker {MQTT_HOST}:{MQTT_PORT} ...")
    client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)

    client.loop_start()
    time.sleep(2)

    simulate_realistic(client, total_cycles=8)

    client.loop_stop()
    client.disconnect()
