import json
import socket
from datetime import datetime
from flask import Flask
from flask_socketio import SocketIO, emit

# Obtener la IP local automáticamenteeeeeeeee asdasdasdasdasdaasdsads
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

app = Flask(__name__)  # Creamos la aplicación Flask
socketio = SocketIO(app, cors_allowed_origins="*", transports=["websocket", "polling"])

@socketio.on("connect")
def handle_connect():
    print("Cliente conectado")

@socketio.on("bus")
def handle_message(data):
    print(f"Bus recibido: {data}")
    
    # Construcción del objeto con la data recibida
    hora_actual = datetime.now().strftime('%H:%M')
    dataBus = {
        "id": "22",
        "company": data.get("company"),
        "destination": data.get("destination"),
        "arrivalTime": hora_actual,
        "boardingGate": data.get("boardingGate"),
    }

    # Enviar la data al frontend
    emit("bus_actualizado", dataBus, broadcast=True)
    print(f"Bus enviado: {dataBus}")

if __name__ == "__main__":
    print(f"Servidor corriendo en http://{local_ip}:5001")
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
