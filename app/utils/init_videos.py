# app/utils/init_videos.py
import os
from sqlalchemy.orm import Session
from app.models import Videos
from app.database import SessionLocal
import asyncio
from app.routers.socketio_videos import broadcast_videos

VIDEOS_DIR = os.path.join("app", "public", "videos")

def init_video_db():
    db: Session = SessionLocal()
    try:
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        files_in_dir = set(os.listdir(VIDEOS_DIR))

        # Registros existentes en la BD
        videos_in_db = db.query(Videos).all()
        filenames_in_db = {v.filename for v in videos_in_db}

        # 1. Agregar archivos nuevos
        max_order = db.query(Videos.order).order_by(Videos.order.desc()).first()
        current_order = max_order[0] if max_order else 0

        new_files = files_in_dir - filenames_in_db
        for filename in sorted(new_files):
            current_order += 1
            new_video = Videos(
                filename=filename,
                title=os.path.splitext(filename)[0],
                description="Auto importado",
                order=current_order
            )
            db.add(new_video)
            print(f"[SYNC] Agregado: {filename}")

        # 2. Eliminar registros huérfanos
        orphan_videos = [v for v in videos_in_db if v.filename not in files_in_dir]
        for video in orphan_videos:
            db.delete(video)
            print(f"[SYNC] Eliminado (archivo faltante): {video.filename}")

        db.commit()
    finally:
        db.close()

    # Disparar broadcast de videos luego de sincronizar
    asyncio.create_task(broadcast_videos())
