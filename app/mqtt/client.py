# app/mqtt/client.py
import json
import threading
import ssl
import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from app.database import SessionLocal
from .config import MQTT_CLIENT_ID, MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, MQTT_KEEPALIVE, MQTT_QOS, MQTT_CA_CERT
from .topics import SUBSCRIBE_TAGS_ALL, SUBSCRIBE_LWT_ALL, SUBSCRIBE_ONLINE_ALL, extract_module_code, topic_status
from .payloads import TagsPayload
from .logic import process_tags_payload, process_lwt_message

class MqttService:
    def __init__(self):
        self.client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True)
        MqttService.instance = self
        self._last_status: dict[str, str] = {}
        if MQTT_USER:
            print(f"👤 Autenticando con usuario MQTT: {MQTT_USER}")
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
        else:
            print("🔓 Conexión MQTT sin TLS")
        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        # Hilo para loop
        self._thread = None
        self._running = False

    # ----------- ciclo de vida -----------
    def start(self):
        print(f"🚀 Conectando a MQTT broker {MQTT_HOST}:{MQTT_PORT} ...")
        self.client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        self._running = True
        self._thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        self._thread.start()
        print("✅ Loop MQTT iniciado en thread separado")

    def stop(self):
        self._running = False
        try:
            self.client.disconnect()
            print("🛑 Conexión MQTT cerrada correctamente")
        except:
            print("⚠️ Error cerrando conexión MQTT")
            pass
    
    # ----------- callbacks -----------
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ MQTT conectado al broker")
            print("📡 Suscribiéndose a tópicos...")
            client.subscribe(SUBSCRIBE_TAGS_ALL, qos=MQTT_QOS)
            client.subscribe(SUBSCRIBE_LWT_ALL, qos=MQTT_QOS)
            client.subscribe(SUBSCRIBE_ONLINE_ALL, qos=MQTT_QOS)
            print(f"   ✔ Suscrito a: {SUBSCRIBE_TAGS_ALL}")
            print(f"   ✔ Suscrito a: {SUBSCRIBE_LWT_ALL}")
            print(f"   ✔ Suscrito a: {SUBSCRIBE_ONLINE_ALL}")
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
                print(f"\n📩 [MQTT] Mensaje recibido")
                print(f"   📌 Topic: {topic}")
                print(f"   📦 Payload crudo: {payload_raw}")
                # Ruteo por sufijo
                if topic.endswith("/TAGS"):
                    # Parsear JSON
                    data = json.loads(payload_raw)
                    payload = TagsPayload(**data)
                    print(f"   ✅ Payload TAGS parseado correctamente")
                    print(f"   🧑‍💻 Módulo: {payload.module_loto_code}")
                    print(f"   👥 Cantidad CARD: {len(payload.tags.get('CARD', []))}")
                    print(f"   🔒 Cantidad LOTO: {len(payload.tags.get('LOTO', []))}")

                    status_payload, publish_topic = process_tags_payload(db, payload)
                    print(f"   📊 Resultado de lógica → Status: {status_payload.status}")

                    if status_payload.status == "alert":
                        for alert in status_payload.alerts:
                            print(f"      🚨 Alerta: {alert.alert_code} - {alert.name} {alert.lastname} → {alert.message}")

                    # Publicar STATUS
                    self.publish_status_if_changed(payload.module_loto_code, status_payload.dict())
                    print(f"   📤 STATUS publicado en {publish_topic}: {status_payload.dict()}")

                # --------- Procesar LWT ---------
                elif topic.endswith("/LWT"):
                    module_code = extract_module_code(topic) or ""
                    # LWT puede ser 'offline' simple
                    status_text = payload_raw.replace('"', '').strip().lower()
                    print(f"   🔌 LWT recibido → módulo {module_code}, estado={status_text}")
                    process_lwt_message(db, module_code, status_text)
                
                # --------- Procesar ONLINE ---------
                elif topic.endswith("/ONLINE"):
                    module_code = extract_module_code(topic) or ""
                    # payload típico: {"module_loto_code":"X","status":"ONLINE"}
                    try:
                        data = json.loads(payload_raw)
                        status_text = str(data.get("status", "ONLINE"))
                    except Exception:
                        status_text = payload_raw
                    print(f"   📡 ONLINE recibido → módulo {module_code}, estado={status_text}")
                    process_lwt_message(db, module_code, status_text)  # reutilizamos el mapeo online/offline
                    
                else:
                    # otros posibles tópicos futuros
                    print("   ❔ Tópico no reconocido")
                    pass

            finally:
                db.close()
        except Exception as e:
            print(f"❌ Error procesando mensaje MQTT: {e}")

    def publish_status_if_changed(self, module_code: str, payload_obj: dict):
        last = self._last_status.get(module_code)
        current = payload_obj.get("status")
        if current != last:
            print(f"   🔄 Cambio de estado detectado: {last} → {current}")
            self.publish_json(topic_status(module_code), payload_obj)
            self._last_status[module_code] = current
        else:
            print(f"   ⏸ Sin cambios de estado (se mantiene {current}), no se publica")

    # ----------- helpers -----------
    def publish_json(self, topic: str, obj: dict):
        payload = json.dumps(obj, ensure_ascii=False)
        print(f"   📤 Publicando en topic={topic}, payload={payload}")
        self.client.publish(topic, payload=payload, qos=MQTT_QOS, retain=False)
