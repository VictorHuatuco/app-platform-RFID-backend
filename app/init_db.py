# app/init.py

import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

# Obtener credenciales desde variables de entorno
pg_host = os.getenv("PG_HOST")
pg_port = os.getenv("PG_PORT")
pg_user = os.getenv("PG_USER")
pg_password = os.getenv("PG_PASSWORD")
pg_database = os.getenv("PG_DATABASE")

app_db_name = os.getenv("APP_DB_NAME")
app_db_user = os.getenv("APP_DB_USER")
app_db_password = os.getenv("APP_DB_PASSWORD")

if None in (pg_host, pg_port, pg_user, pg_password, pg_database, app_db_name, app_db_user, app_db_password):
    raise ValueError("❌ Error: Falta una variable de entorno en el archivo .env.")

# Conectar a PostgreSQL como superusuario
try:
    conn = psycopg2.connect(
        dbname=pg_database,
        user=pg_user,
        password=pg_password,
        host=pg_host,
        port=pg_port
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Comprobar si la base de datos ya existe
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (app_db_name,))
    db_exists = cursor.fetchone()

    if not db_exists:
        cursor.execute(f'CREATE DATABASE "{app_db_name}";')
        print(f"✅ Base de datos '{app_db_name}' creada.")
    else:
        print(f"⚠️ La base de datos '{app_db_name}' ya existe, omitiendo creación.")

    # Comprobar si el usuario ya existe
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", (app_db_user,))
    user_exists = cursor.fetchone()

    if not user_exists:
        cursor.execute(f"CREATE USER {app_db_user} WITH PASSWORD '{app_db_password}';")
        print(f"✅ Usuario '{app_db_user}' creado.")
    else:
        print(f"⚠️ El usuario '{app_db_user}' ya existe, omitiendo creación.")

    # Asignar privilegios en la BD
    cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {app_db_name} TO {app_db_user};")

except Exception as e:
    print(f"❌ Error al configurar la base de datos: {e}")

finally:
    cursor.close()
    conn.close()

# Conectarse a la nueva base de datos
try:
    conn = psycopg2.connect(
        dbname=app_db_name,
        user=pg_user,
        password=pg_password,
        host=pg_host,
        port=pg_port
    )
    cursor = conn.cursor()

    # Asignar permisos en el esquema `public`
    commands_schema = [
        f"GRANT USAGE, CREATE ON SCHEMA public TO {app_db_user};",
        f"ALTER SCHEMA public OWNER TO {app_db_user};",
        f"ALTER DATABASE {app_db_name} OWNER TO {app_db_user};",
    ]

    for command in commands_schema:
        cursor.execute(command)

    conn.commit()
    print("✅ Configuración de la base de datos completada.")

except Exception as e:
    print(f"❌ Error en la configuración final de la base de datos: {e}")

finally:
    cursor.close()
    conn.close()