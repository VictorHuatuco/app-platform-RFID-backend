from .config import MQTT_APP_PREFIX

# Tópicos
# APP/LOTO_RFID/{module_code}/TAGS
# APP/LOTO_RFID/{module_code}/STATUS
# APP/LOTO_RFID/{module_code}/ONLINE
# APP/LOTO_RFID/{module_code}/LWT

def topic_tags(module_code: str) -> str:
    return f"{MQTT_APP_PREFIX}/{module_code}/TAGS"

def topic_status(module_code: str) -> str:
    return f"{MQTT_APP_PREFIX}/{module_code}/STATUS"

def topic_online(module_code: str) -> str:
    return f"{MQTT_APP_PREFIX}/{module_code}/ONLINE"

def topic_lwt(module_code: str) -> str:
    return f"{MQTT_APP_PREFIX}/{module_code}/LWT"

# Patrones de suscripción
SUBSCRIBE_TAGS_ALL = f"{MQTT_APP_PREFIX}/+/TAGS"
SUBSCRIBE_ONLINE_ALL  = f"{MQTT_APP_PREFIX}/+/ONLINE"
SUBSCRIBE_LWT_ALL  = f"{MQTT_APP_PREFIX}/+/LWT"

def extract_module_code(topic: str) -> str | None:
    # Espera: APP/LOTO_RFID/{module}/SUFFIX
    parts = topic.split("/")
    if len(parts) < 3:
        return None
    # parts[0]=APP, [1]=LOTO_RFID, [2]={module}
    return parts[2]
