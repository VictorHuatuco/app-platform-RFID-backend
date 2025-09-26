from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import socket
# comentario
# Obtiene la IP local automáticamente
hostname = socket.gethostname()
local_ip = "192.168.18.219"
# local_ip = socket.gethostbyname(hostname)

app = Flask(__name__)
CORS(app)  # Permite peticiones desde el frontend
socketio = SocketIO(app, cors_allowed_origins="*", transports=["websocket", "polling"])

# Directorio donde están los videos
VIDEO_DIR = os.path.join(os.getcwd(), "videos")

@app.route('/api/videos', methods=["GET"])
def list_videos():
    """ Devuelve la lista de videos disponibles en el servidor """
    try:
        files = os.listdir(VIDEO_DIR)
    except FileNotFoundError:
        return jsonify({"videos": []})
    
    # Filtra solo archivos de video
    videos = [f for f in files if f.lower().endswith(('.mp4', '.webm', '.ogg'))]
    video_urls = [f"http://{local_ip}:5000/videos/{video}" for video in videos]
    
    return jsonify({"videos": video_urls})

@app.route('/videos/<path:filename>')
def serve_video(filename):
    """ Sirve el video desde el directorio local """
    return send_from_directory(VIDEO_DIR, filename)

@socketio.on('connect')
def handle_connect():
    """ Maneja nuevas conexiones desde el frontend """
    print("Cliente conectado")

@socketio.on('get_videos')
def send_videos():
    """ Envía la lista de videos al frontend cuando se solicite por WebSockets """
    print("Evento 'get_videos' recibido")  # Agrega este print para ver si llega la petición
    try:
        files = os.listdir(VIDEO_DIR)
        videos = [f"http://{local_ip}:5000/videos/{f}" for f in files if f.lower().endswith(('.mp4', '.webm', '.ogg'))]
        print("Enviando videos:", videos)
        socketio.emit('videos_list', {"videos": videos})
    except FileNotFoundError:
        print("No se encontraron videos") 
        socketio.emit('videos_list', {"videos": []})

if __name__ == "__main__":
    print(f"Servidor corriendo en: http://{local_ip}:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)