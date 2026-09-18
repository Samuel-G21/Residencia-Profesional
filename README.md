# Sistema de Generación de Documentos de Capacitación (PEMEX / TECNM)

![Arquitectura](https://img.shields.io/badge/Architecture-Docker-blue?style=for-the-badge&logo=docker)
![Backend](https://img.shields.io/badge/Backend-Flask_|_Python-green?style=for-the-badge&logo=python)
![Frontend](https://img.shields.io/badge/Frontend-React_|_Vite-61DAFB?style=for-the-badge&logo=react)
![Base de Datos](https://img.shields.io/badge/Database-MySQL_8.0-orange?style=for-the-badge&logo=mysql)
![Seguridad](https://img.shields.io/badge/Auth-JWT_|_Werkzeug-red?style=for-the-badge)

Sistema integral desarrollado para automatizar y agilizar la gestión de expedientes y generación de documentos de capacitación institucional. La plataforma reduce significativamente los tiempos operativos al extraer información de listas de asistencia en PDF y poblar automáticamente formatos oficiales (.docx y .xlsx) listos para impresión o firma.

---

## ✨ Características Principales

* **Autenticación y Seguridad:** Control de acceso mediante tokens JWT y contraseñas cifradas. Inicialización automática de credenciales de administrador en primer arranque.
* **Extracción Inteligente:** Extracción automatizada de listas de asistencia desde archivos PDF mediante microservicios con *Gotenberg* y *pdfplumber*.
* **Procesamiento de Plantillas:** Generación automatizada de formatos oficiales individuales y grupales (SCPM-04, SCPM-05, SCPM-06, SCPM-07, DC-3, FVC, etc.) utilizando `docxtpl` y `openpyxl`.
* **Cruce de Datos y Catálogos:** Coincidencia de trabajadores con catálogos institucionales para autocompletar CURP, departamentos y datos laborales.
* **Flujo Asistido (Wizard):** Interfaz paso a paso: Carga de lista -> Extracción -> Validación/Edición -> Generación documental.
* **Dashboard Estadístico:** Monitoreo en tiempo real de cursos impartidos, participantes capacitados y métricas visuales con gráficas interactivas.
* **Descarga Consolidada:** Empaquetado automático de todos los documentos generados de un curso en un único archivo `.zip`.

---

## 🛠️ Stack Tecnológico

### Frontend
* **React 19** + **TypeScript / JSX:** Interfaz de usuario reactiva en formato SPA.
* **Vite:** Herramienta de compilación y empaquetado de alta velocidad.
* **Axios:** Cliente HTTP para la comunicación con la API REST.
* **Recharts:** Renderizado de métricas y gráficos estadísticos en el Dashboard.
* **SweetAlert2:** Mensajes emergentes, confirmaciones y alertas dinámicas.
* **Nginx (Alpine):** Servidor web para servir la aplicación en el contenedor de producción.

### Backend
* **Python 3.9+** & **Flask 3.0:** API REST con arquitectura modular por capas.
* **Flask-SQLAlchemy & PyMySQL:** ORM y controlador para base de datos relacional MySQL.
* **PyJWT & Werkzeug:** Emisión y validación de tokens JWT y hashing seguro de contraseñas.
* **Flask-CORS:** Control de acceso entre orígenes para la comunicación frontend-backend.
* **Gunicorn:** Servidor WSGI para despliegue en producción dentro del contenedor.

### Procesamiento Documental & Datos
* **docxtpl:** Motor de inyección de variables basado en Jinja2 para plantillas Word (.docx).
* **openpyxl:** Lectura, manipulación y generación de hojas de cálculo Excel (.xlsx).
* **Pandas & NumPy:** Limpieza, transformación y cruce de datos tabulares.
* **pdfplumber & pypdf:** Extracción estructurada de tablas y texto desde documentos PDF.

### Infraestructura & Contenedores
* **Docker & Docker Compose:** Orquestación y ejecución de servicios aislados.
* **MySQL 8.0:** Base de datos relacional para persistencia de cursos, historial, usuarios y catálogos.
* **Gotenberg 8:** Microservicio para conversión y procesamiento documental vía API.

---

## 🌐 Servicios y Mapeo de Puertos

| Servicio | Contenedor | Puerto Host | Puerto Interno | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | `pemex_frontend` | `3000` | `80` (Nginx) | Interfaz web de usuario |
| **Backend API** | `pemex_backend` | `5000` | `5000` (Gunicorn) | Endpoints REST y lógica de negocio |
| **Microservicio PDF** | `pemex_gotenberg` | `3001` | `3000` | Procesamiento y conversión de PDFs |
| **Base de Datos** | `pemex_mysql` | `3307` | `3306` | Servidor MySQL 8.0 |

---

## 🔑 Credenciales por Defecto

### Acceso a la Plataforma Web (Login)
* **Usuario:** `admin`
* **Contraseña:** `admin`

> [!NOTE]
> El usuario administrador se crea automáticamente al iniciar el backend si la base de datos se encuentra vacía.

### Base de Datos (MySQL)
* **Host:** `localhost` (o `db` dentro de la red de Docker)
* **Puerto:** `3307`
* **Usuario:** `pemex_user`
* **Contraseña:** `pemex_password`
* **Base de datos:** `pemex_db`
* **Contraseña Root:** `rootpassword`

---

## 🚀 Instalación y Despliegue

### 1. Requisitos Previos
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) en ejecución.
* [Docker Compose](https://docs.docker.com/compose/) v2+.

### 2. Configuración de Variables de Entorno (Opcional)
Si deseas personalizar las contraseñas de la base de datos, copia el archivo de ejemplo:
```bash
cp .env.example .env
```

### 3. Levantar los Servicios
En la raíz del proyecto, ejecuta:
```bash
docker-compose up -d --build
```
Este comando construirá las imágenes del frontend y backend, descargará los servicios auxiliares e inicializará la base de datos con [`init.sql`](./init.sql).

### 4. Acceder al Sistema
Abre tu navegador e ingresa a:
👉 **[http://localhost:3000](http://localhost:3000)**

---

## 📖 Flujo de Trabajo del Sistema

1. **Cargar Catálogos:** En el módulo *"Cargar Catálogos"*, sube el archivo Excel base que contiene el padrón de trabajadores y CURPs para alimentar la base de datos.
2. **Generación de Expediente:**
   * Ve a *"Gestión de Expedientes"*.
   * **Paso 1:** Sube la lista de asistencia en formato PDF para extraer los participantes a Excel.
   * **Paso 2:** Ingresa los metadatos del evento (nombre, instructor, fechas) y selecciona los formatos requeridos (*SCPM-04, 05, 06, 07, DC-3*, etc.).
   * **Paso 3:** Confirma los datos y descarga el paquete consolidado en formato `.zip`.
3. **Historial y Estadísticas:** Consulta el módulo *"Historial"* para reimpresiones o auditoría, y el *"Dashboard"* para visualizar métricas globales.

---

## 📂 Estructura del Proyecto

```text
├── backend/
│   ├── app/
│   │   ├── controllers/      # Controladores de rutas REST (auth, cursos, archivos, etc.)
│   │   ├── models/           # Modelos de SQLAlchemy (cursos, historial, usuarios, etc.)
│   │   ├── routes/           # Registro centralizado de Blueprints
│   │   ├── schemas/          # Validación y serialización con Marshmallow
│   │   ├── services/         # Lógica de negocio (extracción PDF, generación Word/Excel)
│   │   ├── utils/            # Utilidades auxiliares
│   │   ├── config.py         # Configuración de la aplicación y base de datos
│   │   └── __init__.py       # Factoría de la app Flask e inicialización de esquemas
│   ├── catalogos/            # Archivos y fuentes de catálogos base
│   ├── templates/            # Plantillas oficiales en .docx y .xlsx
│   ├── create_user.py        # Script manual para creación de usuarios
│   ├── requirements.txt      # Dependencias de Python
│   ├── run.py                # Punto de entrada de la API Flask
│   └── Dockerfile            # Construcción de la imagen backend con Gunicorn
├── frontend/
│   ├── src/
│   │   ├── assets/           # Recursos visuales e íconos
│   │   ├── components/       # Componentes reutilizables (Navbar, Cards, Modales)
│   │   ├── pages/            # Vistas principales (Dashboard, Generador, Historial)
│   │   ├── services/         # Servicios Axios para conexión con la API
│   │   ├── App.jsx           # Enrutamiento y flujo principal
│   │   └── index.jsx         # Punto de montaje de React
│   ├── package.json          # Dependencias de Node.js
│   └── Dockerfile            # Multi-stage build (Vite -> Nginx)
├── .env.example              # Plantilla de variables de entorno
├── docker-compose.yml        # Orquestación de los 4 contenedores
└── init.sql                  # Script SQL inicial de tablas y estructura
```
