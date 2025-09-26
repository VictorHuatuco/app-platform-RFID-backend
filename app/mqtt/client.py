# app/mqtt/client.py
import json
import threading
import ssl
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from app.database import SessionLocal
from .config import MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, MQTT_KEEPALIVE, MQTT_QOS, MQTT_CA_CERT
from .topics import SUBSCRIBE_TAGS_ALL, SUBSCRIBE_LWT_ALL, SUBSCRIBE_ONLINE_ALL, extract_module_code, topic_status
from .payloads import TagsPayload
from .logic import process_tags_payload, process_lwt_message

class MqttService:
    def __init__(self):
        self.client = mqtt.Client(client_id="app-backend-subscriber", clean_session=True)
        if MQTT_USER:
            self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD or None)

        # Configurar TLS si existe CA_CERT
        if MQTT_CA_CERT:
            self.client.tls_set(
                ca_certs=MQTT_CA_CERT,
                certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            print(f"🔒 TLS habilitado usando CA: {MQTT_CA_CERT}")

        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        # Hilo para loop
        self._thread = None
        self._running = False

    # ----------- ciclo de vida -----------
    def start(self):
        self.client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        self._running = True
        self._thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        try:
            self.client.disconnect()
        except:
            pass

    # ----------- callbacks -----------
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            # Suscribir a TAGS y LWT
            client.subscribe(SUBSCRIBE_TAGS_ALL, qos=MQTT_QOS)
            client.subscribe(SUBSCRIBE_LWT_ALL, qos=MQTT_QOS)
            client.subscribe(SUBSCRIBE_ONLINE_ALL, qos=MQTT_QOS)
            print("✅ MQTT conectado y suscrito.")
        else:
            print(f"❌ Error de conexión MQTT: rc={rc}")

    def _on_disconnect(self, client, userdata, rc):
        print(f"⚠️ MQTT desconectado (rc={rc})")

    def _on_message(self, client, userdata, msg):
        try:
            # Abrir sesión por mensaje (thread-safe)
            db: Session = SessionLocal()
            try:
                topic = msg.topic
                payload_raw = msg.payload.decode("utf-8", errors="ignore").strip()

                # Ruteo por sufijo
                if topic.endswith("/TAGS"):
                    # Parsear JSON
                    data = json.loads(payload_raw)
                    payload = TagsPayload(**data)
                    status_payload, publish_topic = process_tags_payload(db, payload)

                    # Publicar STATUS
                    self.publish_json(publish_topic, status_payload.dict())

                elif topic.endswith("/LWT"):
                    module_code = extract_module_code(topic) or ""
                    # LWT puede ser 'offline' simple
                    status_text = payload_raw.replace('"', '').strip().lower()
                    process_lwt_message(db, module_code, status_text)

                else:
                    # otros posibles tópicos futuros
                    pass

            finally:
                db.close()
        except Exception as e:
            print(f"❌ Error procesando mensaje MQTT: {e}")

    # ----------- helpers -----------
    def publish_json(self, topic: str, obj: dict):
        payload = json.dumps(obj, ensure_ascii=False)
        self.client.publish(topic, payload=payload, qos=MQTT_QOS, retain=False)
