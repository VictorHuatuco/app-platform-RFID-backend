# 🚍 App LOTO Backend

Este proyecto es una API backend para una plataforma de control del seguimiento de LOTO, desarrollada con **FastAPI**, **PostgreSQL** y **SQLAlchemy**.

---

## 📌 Requisitos previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- [Python 3.8+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Git](https://git-scm.com/downloads)

---

## 📥 Instalación

Sigue estos pasos para instalar y configurar el proyecto en tu entorno local.

### 1️⃣ Clonar el repositorio

Abre una terminal y ejecuta el siguiente comando:

``` bash
git clone https://github.com/VictorHuatuco/app-terminal-backend.git
```
Luego, accede a la carpeta del proyecto:

``` bash
cd app-backend
```
### 2️⃣ Crear y activar el entorno virtual
Para mantener organizadas las dependencias, crea un entorno virtual:

``` bash
python -m venv venv
```
Luego, actívalo según tu sistema operativo:

``` bash
source venv/Scripts/activate
```

### 3️⃣ Instalar las dependencias del proyecto
Una vez activado el entorno virtual, instala las dependencias con:

``` bash
pip install -r requirements.txt
```
Esto descargará e instalará automáticamente todas las librerías necesarias para el proyecto.

## 🗄 Configuración de la base de datos
### 4️⃣ Instalar PostgreSQL
Si aún no tienes PostgreSQL instalado, descárgalo e instálalo.
🔹 Importante: Durante la instalación, se te pedirá que configures una contraseña para el usuario postgres. Recuerda esta contraseña, ya que la necesitarás más adelante.

### 5️⃣ Configurar las variables de entorno
Crea un archivo .env en la carpeta raíz del proyecto y copia el siguiente contenido:

```env
# Configuración de PostgreSQL
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=*******  # Reemplaza con la contraseña de PostgreSQL
PG_DATABASE=postgres

# Configuración de la base de datos de la app
APP_DB_NAME=terminal_db
APP_DB_USER=admin_terminal_app
APP_DB_PASSWORD=123456
```
🔹 Nota: Asegúrate de reemplazar PG_PASSWORD con la contraseña que configuraste en PostgreSQL.

🚀 Inicialización del sistema
### 6️⃣ Inicializar la base de datos
Ejecuta el siguiente comando para crear la base de datos:

```bash
python -m app.init_db
```
### 7️⃣ Crear las tablas en la base de datos y la semilla de datos
```bash
python -m app.create_db
```

###  ▶️ Ejecución del servidor
Para iniciar la API, ejecuta:
```bash
uvicorn app.main:app --reload
```
El backend estará disponible en:
🔗 http://127.0.0.1:8000

### 📄 Documentación de la API
FastAPI genera automáticamente la documentación en:

📜 Swagger UI: http://127.0.0.1:8000/docs
📄 Redoc: http://127.0.0.1:8000/redoc

###💡 Notas adicionales
Si tienes problemas con dependencias, intenta:

```bash
pip install --upgrade pip
```

Para salir del entorno virtual:
```bash
deactivate
```




## 📂 Estructura del proyecto

(app-backend/)
│── app/
│ ├── create_db.py # Script para crear y resetear las tablas de la BD
│ ├── database.py # Conexión y helpers para la BD
│ ├── init_db.py # Crea la BD con el usuario
│ ├── main.py # Punto de entrada de la API
│ ├── models.py # Modelos SQLAlchemy
│ ├── schemas.py # Esquemas Pydantic
│ ├── seed.py # Script para cargar datos iniciales
│ ├── routers/ # Carpeta con endpoints
│ │ ├── alerts.py # Rutas de alertas
│ │ ├── bahia.py # Rutas de bahías
│ │ ├── headquarters.py # Rutas de sedes
│ │ ├── maintenance.py # Rutas de mantenimientos
│ │ ├── people_in_maintenance.py # Rutas de personas en mantenimiento
│ │ ├── status_bahia.py # Rutas de estados de bahía
│ │ ├── tags.py # Rutas de tags
│ │ ├── type_alerts.py # Rutas de tipos de alertas
│ │ ├── type_tags.py # Rutas de tipos de tag
│ │ ├── users.py # Rutas de usuarios
│ ├── public/ # Archivos estáticos
│
│── postman/ #Carpeta para probar las APIs con Postman
├── requirements.txt # Dependencias
├── .env # Variables de entorno
└── README.md # Documentación

Copiar código
