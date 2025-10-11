# app/mqtt/logic.py

from sqlalchemy.orm import Session
from typing import List, Tuple
from app import models
from .payloads import TagsPayload, StatusPayload, StatusAlertItem
from .topics import topic_status
from .config import MQTT_QOS
import json
from datetime import datetime, timedelta, timezone
import random
import string

WINDOW_MINUTES = 10

def _get_users_by_tags(db: Session, tag_codes: List[str], required_type: str) -> List[models.User]:
    """
    Devuelve usuarios que poseen tags (tags.tag_code IN tag_codes) y cuyo TypeTag.name == required_type.
    required_type: "CARD" o "LOTO".
    """
    if not tag_codes:
        return []

    users = (
        db.query(models.User)
        .join(models.Tag, models.Tag.id_users == models.User.id)
        .join(models.TypeTag, models.TypeTag.id == models.Tag.id_type_tag)
        .filter(models.Tag.tag_code.in_(tag_codes))
        .filter(models.TypeTag.name == required_type)
        .all()
    )
    print(f"🔎 _get_users_by_tags → type={required_type}, encontrados={len(users)}")
    for u in users:
        print(f"   👤 {u.id} - {u.name} {u.lastname} (tag_type={required_type})")

    # Join: Tag -> TypeTag -> User
    return users

def _upsert_type_alert(db: Session, name: str) -> models.TypeAlert:
    ta = db.query(models.TypeAlert).filter(models.TypeAlert.name == name).first()
    if not ta:
        ta = models.TypeAlert(name=name)
        db.add(ta)
        db.commit()
        db.refresh(ta)
        print(f"🆕 Creado nuevo TypeAlert: {name}")
    return ta

def _create_alerts_for_violators(
    db: Session,
    violators: List[models.User],
    bahia: models.Bahia,
    reason_type_alert_name: str = "Ingreso sin candado"
):
    """
    Opcional: crear registros en 'alerts' para cada infractor, si hay un mantenimiento activo.
    Si no quieres persistir, puedes omitir este bloque.
    """
    if not violators:
        return

    print(f"🚨 Creando {len(violators)} alertas en BD para bahía={bahia.id}, motivo={reason_type_alert_name}")
    type_alert = _upsert_type_alert(db, reason_type_alert_name)

    # Heurística simple: si hay maintenances en esa bahía, toma la última
    maintenance = (
        db.query(models.Maintenance)
        .filter(models.Maintenance.id_bahias == bahia.id)
        .order_by(models.Maintenance.id.desc())
        .first()
    )
    if not maintenance:
        print("⚠️ No se encontró mantenimiento activo en esta bahía, no se registran alertas.")
        return  # no hay mantenimiento asociado

    now_t = datetime.now(timezone.utc)
    for user in violators:
        # hallamos PeopleInMaintenance (si existe) para vincular; si no, lo omitimos
        pim = (
            db.query(models.PeopleInMaintenance)
            .filter(
                models.PeopleInMaintenance.id_users == user.id,
                models.PeopleInMaintenance.id_maintenance == maintenance.id
            )
            .order_by(models.PeopleInMaintenance.id.desc())
            .first()
        )

        db_alert = models.Alert(
            alert_time=now_t,
            id_maintenance=maintenance.id,
            id_people_in_maintenance=pim.id if pim else None,
            id_types_alerts=type_alert.id,
            resolved=False,
        )
        db.add(db_alert)
        print(f"   ✅ Alerta registrada para {user.name} {user.lastname}, maintenance={maintenance.id}, pim_id={pim.id if pim else 'N/A'}")
    db.commit()

def _parse_ts(ts: str) -> datetime | None:
    try:
        # "2025-09-07T12:34:56Z"
        return datetime.fromisoformat(ts.replace("Z","+00:00"))
    except Exception as e:
        print(f"⚠️ Error parseando timestamp {ts}: {e}")
        return None

def _get_tag_user_info(db: Session, tag_codes: List[str]) -> List[dict]:
    """
    Devuelve información básica de cada tag leído:
    [
        {tag_code, type, user_name, user_lastname, registered (bool)}
    ]
    Si el tag no pertenece a ningún usuario registrado, se devuelve con registered=False.
    """
    if not tag_codes:
        return []

    # Buscar tags registrados con sus usuarios y tipos
    results = (
        db.query(
            models.Tag.tag_code,
            models.TypeTag.name.label("type_name"),
            models.User.name.label("user_name"),
            models.User.lastname.label("user_lastname")
        )
        .join(models.TypeTag, models.TypeTag.id == models.Tag.id_type_tag)
        .join(models.User, models.User.id == models.Tag.id_users)
        .filter(models.Tag.tag_code.in_(tag_codes))
        .distinct()
        .all()
    )

    found_tag_codes = {r.tag_code for r in results}

    # Armar lista para tags conocidos
    info = []
    for tag_code, type_name, user_name, user_lastname in results:
        info.append({
            "tag_code": tag_code,
            "type": type_name,
            "user_name": user_name,
            "user_lastname": user_lastname,
            "registered": True
        })

    # Agregar los tags no registrados
    for tag_code in tag_codes:
        if tag_code not in found_tag_codes:
            info.append({
                "tag_code": tag_code,
                "type": None,
                "user_name": None,
                "user_lastname": None,
                "registered": False
            })

    return info




def process_tags_payload(db: Session, payload: TagsPayload) -> Tuple[StatusPayload, str]:
    """
    Procesa un payload TAGS:
    - Actualiza bahía (online).
    - Gestiona mantenimiento según LOTOs detectados.
    - Determina infractores (CARD sin LOTO).
    - Publica STATUS con resultado.
    Retorna (status_payload, topic_de_publicacion)
    """
    print(f"\n📥 Procesando TAGS payload para módulo={payload.module_loto_code}")

    # 1) Ubicar la bahía
    bahia = (
        db.query(models.Bahia)
        .filter(models.Bahia.module_loto_code == payload.module_loto_code)
        .first()
    )
    if not bahia:
        print(f"❌ No se encontró bahía con module_loto_code={payload.module_loto_code}")
        status = StatusPayload(
            module_loto_code=payload.module_loto_code,
            status="error",
            message="module_loto_code no asignado a ninguna bahía"
        )
        return status, topic_status(payload.module_loto_code)

    # 2) Marcar módulo online
    bahia.module_loto_status = "online"
    db.commit()
    print(f"   ✅ Bahía {bahia.id} marcada como ONLINE")

    # 3) Extraer tags
    card_codes = [t.tag_code for t in payload.tags.get("CARD", [])]
    loto_codes = [t.tag_code for t in payload.tags.get("LOTO", [])]
    now = datetime.now(timezone.utc)

    print(f"   👥 Cards detectados={len(card_codes)}, Lotos detectados={len(loto_codes)}")

    # 4) Obtener usuarios por tipo
    card_users = _get_users_by_tags(db, card_codes, "CARD")
    loto_users = _get_users_by_tags(db, loto_codes, "LOTO")

    card_user_ids = {u.id for u in card_users}
    loto_user_ids = {u.id for u in loto_users}
    print(f"   📊 card_user_ids={card_user_ids}, loto_user_ids={loto_user_ids}")

    # 📦 Generar información de tags detectados
    all_tags = card_codes + loto_codes
    tags_info = _get_tag_user_info(db, all_tags)

    # Publicar información de usuarios por tag
    if tags_info:
        user_info_payload = {
            "module_loto_code": payload.module_loto_code,
            "timestamp": now.isoformat(),
            "tags_info": tags_info
        }

    topic_users = f"APP/LOTO_RFID/{payload.module_loto_code}/USERS"
    print(f"📤 Publicando info de tags detectados en {topic_users}")
    try:
        from .client import MqttService
        if MqttService.instance:
            MqttService.instance.publish_json(topic_users, user_info_payload)
            print("✅ Info de tags enviada correctamente al ESP32")
        else:
            print("⚠️ MqttService.instance no está inicializado")
    except Exception as e:
        print(f"⚠️ Error publicando tags_info: {e}")

    # 5) Buscar mantenimiento activo
    maintenance = (
        db.query(models.Maintenance)
        .filter(models.Maintenance.id_bahias == bahia.id, models.Maintenance.end_time.is_(None))
        .first()
    )

    # 6) Si hay LOTOs y no hay mantenimiento → crear uno
    if loto_users or card_codes and not maintenance: ####### CONSULTAR SI SE VA A CREAR EL MANTENIMIENTO CUANDO SE DETECTA EN ALGUNO DE LAS STATIONs
        maintenance = models.Maintenance(
            name=_generate_maintenance_name(),
            id_bahias=bahia.id,
            start_time=now,
            status="active"
        )
        db.add(maintenance)
        db.commit()
        db.refresh(maintenance)
        print(f"🛠️ Nuevo mantenimiento iniciado en bahía {bahia.id}")

    # 7) Actualizar PeopleInMaintenance para usuarios con LOTO
    if maintenance:
        # Insertar/asegurar entradas activas
        for user in loto_users:
            pim = (
                db.query(models.PeopleInMaintenance)
                .filter_by(id_users=user.id, id_maintenance=maintenance.id, exit_time=None)
                .first()
            )
            if not pim:
                db.add(models.PeopleInMaintenance(
                    id_users=user.id,
                    id_maintenance=maintenance.id,
                    entry_time=now
                ))
                print(f"   🔒 {user.name} {user.lastname} agregó su candado")
        
        # Cerrar entradas de quienes ya no aparecen
        current_ids = {u.id for u in loto_users}
        active_pims = (
            db.query(models.PeopleInMaintenance)
            .filter_by(id_maintenance=maintenance.id, exit_time=None)
            .all()
        )
        for pim in active_pims:
            if pim.id_users not in current_ids:
                pim.exit_time = now
                print(f"   🔓 Usuario {pim.id_users} retiró su candado")

        # Si no queda ningún LOTO → cerrar mantenimiento
        if not loto_users:
            maintenance.end_time = now
            maintenance.status = "finished"
            print(f"✅ Mantenimiento finalizado en bahía {bahia.id}")

        db.commit()

    # 8) Revisar infractores (CARD sin su LOTO)
    violator_ids = card_user_ids - loto_user_ids
    violators = [u for u in card_users if u.id in violator_ids]

    if violators:
        print(f"🚨 {len(violators)} violadores detectados")
        _create_alerts_for_violators(db, violators, bahia, reason_type_alert_name="Ingreso sin candado")

        alerts = [
            StatusAlertItem(
                alert_code="NO_LOTO",
                name=u.name,
                lastname=u.lastname,
                message="Ingresó sin colocar candado."
            )
            for u in violators
        ]
        status = StatusPayload(
            module_loto_code=payload.module_loto_code,
            status="alert",
            alerts=alerts
        )
    else:
        print("✅ Todos los trabajadores tienen LOTO válido")
        status = StatusPayload(
            module_loto_code=payload.module_loto_code,
            status="ok",
            message="Todos los trabajadores con candado validado."
        )

    return status, topic_status(payload.module_loto_code)


def process_lwt_message(db: Session, module_code: str, status_text: str):
    """
    Procesa LWT/estado del módulo (por ejemplo 'offline').
    """
    print(f"\n🔌 Procesando LWT/ONLINE → módulo={module_code}, status_text={status_text}")
    bahia = (
        db.query(models.Bahia)
        .filter(models.Bahia.module_loto_code == module_code)
        .first()
    )
    if not bahia:
        return

    status_map = {"offline": "offline", "online": "online", "error": "error"}
    bahia.module_loto_status = status_map.get(status_text.lower(), "offline")
    db.commit()
    print(f"   ✅ Estado de bahía {bahia.id} actualizado a {bahia.module_loto_status}")


def _generate_maintenance_name() -> str:
    """Genera un nombre aleatorio tipo MT001234."""
    random_number = ''.join(random.choices(string.digits, k=6))
    return f"MT-{random_number}"