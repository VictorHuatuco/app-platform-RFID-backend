from sqlalchemy.orm import Session
from typing import List, Tuple
from app import models
from .payloads import TagsPayload, StatusPayload, StatusAlertItem
from .topics import topic_status
from .config import MQTT_QOS
import json
from datetime import datetime

def _get_users_by_tags(db: Session, tag_codes: List[str], required_type: str) -> List[models.User]:
    """
    Devuelve usuarios que poseen tags (tags.tag_code IN tag_codes) y cuyo TypeTag.name == required_type.
    required_type: "CARD" o "LOTO".
    """
    if not tag_codes:
        return []

    # Join: Tag -> TypeTag -> User
    return (
        db.query(models.User)
        .join(models.Tag, models.Tag.id_users == models.User.id)
        .join(models.TypeTag, models.TypeTag.id == models.Tag.id_type_tag)
        .filter(models.Tag.tag_code.in_(tag_codes))
        .filter(models.TypeTag.name == required_type)
        .all()
    )

def _upsert_type_alert(db: Session, name: str) -> models.TypeAlert:
    ta = db.query(models.TypeAlert).filter(models.TypeAlert.name == name).first()
    if not ta:
        ta = models.TypeAlert(name=name)
        db.add(ta)
        db.commit()
        db.refresh(ta)
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

    type_alert = _upsert_type_alert(db, reason_type_alert_name)

    # Heurística simple: si hay maintenances en esa bahía, toma la última
    maintenance = (
        db.query(models.Maintenance)
        .filter(models.Maintenance.id_bahias == bahia.id)
        .order_by(models.Maintenance.id.desc())
        .first()
    )
    if not maintenance:
        return  # no hay mantenimiento asociado

    now_t = datetime.now().time()
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
    db.commit()

def process_tags_payload(db: Session, payload: TagsPayload) -> Tuple[StatusPayload, str]:
    """
    Procesa un payload TAGS:
    - Actualiza bahía (online).
    - Determina infractores (CARD sin LOTO).
    - Publica STATUS con resultado.
    Retorna (status_payload, topic_de_publicacion)
    """
    # 1) Ubicar la bahía por module_loto_code
    bahia = (
        db.query(models.Bahia)
        .filter(models.Bahia.module_loto_code == payload.module_loto_code)
        .first()
    )
    if not bahia:
        # No existe el mapeo -> error
        status = StatusPayload(
            module_loto_code=payload.module_loto_code,
            status="error",
            message="module_loto_code no asignado a ninguna bahía"
        )
        return status, topic_status(payload.module_loto_code)

    # 2) Marcar módulo online (último visto al recibir datos)
    bahia.module_loto_status = "online"
    db.commit()

    # 3) Extraer listas de códigos
    card_codes = [t.tag_code for t in payload.tags.get("CARD", [])]
    loto_codes = [t.tag_code for t in payload.tags.get("LOTO", [])]

    # 4) Obtener usuarios por cada tipo
    card_users = _get_users_by_tags(db, card_codes, "CARD")
    loto_users = _get_users_by_tags(db, loto_codes, "LOTO")

    card_user_ids = {u.id for u in card_users}
    loto_user_ids = {u.id for u in loto_users}

    # 5) Infractores = CARD presentados - LOTO presentados (por usuario)
    violator_ids = card_user_ids - loto_user_ids
    violators = [u for u in card_users if u.id in violator_ids]

    if violators:
        # Persistir (opcional) alertas
        _create_alerts_for_violators(db, violators, bahia, reason_type_alert_name="Ingreso sin candado")

        alerts = [
            StatusAlertItem(name=u.name, lastname=u.lastname, message="Ingresó sin colocar candado.")
            for u in violators
        ]
        status = StatusPayload(
            module_loto_code=payload.module_loto_code,
            status="alert",
            alerts=alerts
        )
    else:
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
