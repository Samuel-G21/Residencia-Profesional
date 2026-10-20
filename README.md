# Sistema de Generación de Documentos de Capacitación (PEMEX / TECNM)

![Arquitectura](https://img.shields.io/badge/Architecture-Docker-blue?style=for-the-badge&logo=docker)
![Backend](https://img.shields.io/badge/Backend-Flask_|_Python-green?style=for-the-badge&logo=python)
![Frontend](https://img.shields.io/badge/Frontend-React_|_Vite-61DAFB?style=for-the-badge&logo=react)
![Base de Datos](https://img.shields.io/badge/Database-MySQL_8.0-orange?style=for-the-badge&logo=mysql)
![Seguridad](https://img.shields.io/badge/Auth-JWT_|_Werkzeug-red?style=for-the-badge)

Sistema integral desarrollado para automatizar y agilizar la gestión de expedientes y la generación de documentos oficiales de capacitación institucional en PEMEX (Desarrollo Humano - Refinería Tula). La plataforma extrae información desde listas de asistencia en formato PDF (`SCPM-01`), cruza datos con catálogos maestros (`CURP` y `STPS`), pobla automáticamente plantillas oficiales en Word (`.docx`) y Excel (`.xlsx` / `.xlsm`), y consolida los expedientes listos para impresión o firma junto con un panel de análisis estadístico.

---

## Características Principales

* **Autenticación y Seguridad:** Control de acceso mediante tokens JWT (`HS256`), contraseñas cifradas con Werkzeug, cierre automático de sesión por inactividad (15 minutos), bloqueo temporal ante intentos fallidos de inicio de sesión, protección contra Path Traversal y renderizado de plantillas en entorno aislado (`SandboxedEnvironment` de Jinja2).
* **Extracción Automatizada de PDF (`SCPM-01`):** Lectura estructurada de tablas y metadatos de listas de asistencia en PDF mediante `pdfplumber` para generar automáticamente la guía de asistencia en Excel (`.xlsx`).
* **Motor de Plantillas Word y Excel:** Generación masiva de formatos individuales por trabajador y grupales por evento (`Cédula de Registro`, `DC-3`, `SCPM-03`, `SCPM-04`, `SCPM-05`, `SCPM-05A`, `SCPM-06`, `SCPM-07`, `FVC`, `Carta Compromiso`, `Informe Técnico`, `SIRCE_Automatizado.xlsm`) utilizando `docxtpl` y `openpyxl`.
* **Gestor Dinámico de Plantillas:** Carga de nuevas plantillas `.docx`, `.xlsx`, `.xlsm` o `.xls` desde la interfaz web con conversión automática de etiquetas simples (`[FICHA]`, `[NOMBRE_COMPLETO]`, etc.) a variables Jinja2 (`{{ ficha }}`, `{{ nombre_completo }}`).
* **Control de Ciclo de Vida del Evento:** Seguimiento en 5 fases (*Registro/Programación*, *Ejecución*, *Extracción SCPM-01*, *Integración de Expediente* y *Cierre/Firmas*), alta manual de trabajadores adicionales, registro de bajas (`BAJA`) y reprobados (`NO APTO`), carga de calificaciones (`SCPM-07`) y exportación de constancias `STPS`.
* **Consolidación en PDF Maestro y ZIP:** Conversión automática de documentos Word a PDF mediante el microservicio *Gotenberg*, unión en un único archivo PDF maestro con `pypdf` y empaquetado organizado por carpetas en un archivo `.zip`.
* **Dashboard Estadístico:** Monitoreo de indicadores clave (KPIs), plan de acción automático según el índice de reprobación, métricas demográficas por género (calculadas a partir de la CURP) y exportación a `.csv` e imagen `.png`.

---

## Stack Tecnológico

### Frontend
* **React 19 + TypeScript (`.tsx`):** Interfaz de usuario tipo SPA dividida por vistas funcionales.
* **Vite:** Servidor de desarrollo y empaquetador de producción.
* **Axios:** Cliente HTTP con interceptor global para inyección de token JWT.
* **Recharts & html2canvas:** Visualización de gráficas interactivas y exportación del dashboard a imagen.
* **SweetAlert2:** Notificaciones y diálogos de confirmación.
* **Nginx (Alpine):** Servidor web estático para el contenedor de producción.

### Backend
* **Python 3.9+ & Flask 3.0:** API REST estructurada bajo el patrón *Application Factory* y *Blueprints*.
* **Flask-SQLAlchemy & PyMySQL:** ORM y conector para persistencia en MySQL 8.0.
* **PyJWT & Werkzeug Security:** Emisión/validación de tokens JWT y hashing de contraseñas.
* **docxtpl, openpyxl, pandas, pdfplumber, pypdf:** Procesamiento documental y tabular.
* **Gunicorn:** Servidor WSGI de producción.

### Infraestructura
* **Docker & Docker Compose:** Orquestación de 4 contenedores (`db`, `gotenberg`, `api`, `interfaz`).
* **MySQL 8.0:** Base de datos relacional (`pemex_db`).
* **Gotenberg 8:** Microservicio con LibreOffice para conversión de documentos `.docx` a `.pdf`.

---

## Servicios y Mapeo de Puertos

| Servicio | Contenedor | Puerto Host | Puerto Interno | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | `pemex_frontend` | `3000` | `80` (Nginx) | Interfaz web de usuario |
| **Backend API** | `pemex_backend` | `5000` | `5000` (Gunicorn) | Endpoints REST y motor documental |
| **Microservicio PDF** | `pemex_gotenberg` | `3001` | `3000` | Conversión de Word a PDF |
| **Base de Datos** | `pemex_mysql` | `3307` | `3306` | Servidor MySQL 8.0 |

---

## Credenciales por Defecto

### Acceso a la Plataforma Web (Login)
* **Usuario:** `admin`
* **Contraseña:** `admin`

> [!NOTE]
> El usuario administrador se crea automáticamente al iniciar el backend si no existe en la base de datos. También puede verificarse o crearse manualmente ejecutando `python create_user.py` dentro del contenedor o entorno del backend.

### Base de Datos (MySQL)
* **Host:** `localhost` (o `db` dentro de la red de Docker)
* **Puerto:** `3307` (Host) / `3306` (Contenedor)
* **Usuario:** `pemex_user`
* **Contraseña:** `pemex_password`
* **Base de datos:** `pemex_db`
* **Contraseña Root:** `rootpassword`

---

## Instalación y Despliegue

### 1. Requisitos Previos
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) en ejecución.
* [Docker Compose](https://docs.docker.com/compose/) v2+.

### 2. Configuración de Variables de Entorno (Opcional)
Para personalizar credenciales o parámetros del entorno, copia el archivo de ejemplo en la raíz del proyecto:
```bash
cp .env.example .env
```

### 3. Levantar los Servicios
Desde la raíz del proyecto, ejecuta:
```bash
docker-compose up -d --build
```
Este comando construirá las imágenes del frontend y backend, levantará MySQL 8.0 y Gotenberg 8, e inicializará automáticamente las tablas mediante SQLAlchemy.

### 4. Acceder al Sistema
Abre tu navegador web en:
**[http://localhost:3000](http://localhost:3000)**

---

## Flujo de Trabajo del Sistema

1. **Actualizar Catálogos (`Actualizar Catálogos`):** Sube el archivo Excel del padrón maestro (`CURP.xlsx` con columnas `FICHA` y `CURP`) o los catálogos `STPS` para mantener sincronizada la base de datos.
2. **Gestión de Expedientes (`Gestión de Expedientes`):**
   * **Paso 1 (Extracción PDF a Excel):** Sube el PDF oficial de asistencia (`SCPM-01`) para extraer y descargar automáticamente la guía en formato `.xlsx`. Revísala antes de continuar.
   * **Paso 2 (Generación de Documentos):** Ingresa el ID del evento, sube el Excel validado (y opcionalmente el `SCPM-03.docx` lleno para extraer el Supervisor Técnico), selecciona el tipo de curso (*Actualización* o *Ascenso*) y marca los formatos requeridos.
   * **Paso 3 (Descarga de Expediente):** Descarga el paquete consolidado `Expediente_<id_evento>.zip`, que contiene las carpetas clasificadas y el archivo `<id_evento>_PDF_Maestro.pdf`.
3. **Seguimiento y Evaluación (`Historial de Eventos` -> `Detalles`):**
   * Agrega participantes adicionales de forma manual o registra estados de `BAJA` y `NO APTO`.
   * Descarga el formato `SCPM-07` prellenado (paginado automáticamente de 5 en 5 trabajadores por hoja), súbelo con las calificaciones finales y exporta el archivo macro-habilitado `STPS_<id_evento>.xlsm`.
   * Finaliza o cancela el evento cuando concluya su proceso administrativo.
4. **Monitoreo (`Dashboard Estadístico`):** Consulta KPIs, gráficas de rendimiento y distribución por género, o exporta los resultados en `.csv` y `.png`. Para más detalles operativos consulta el archivo [`manual_de_usuario.md`](./manual_de_usuario.md).

---

## Estructura del Proyecto

```text
├── .github/
│   └── workflows/
│       └── ci.yml                  # Pipeline CI/CD (Pytest para Backend y Jest para Frontend)
├── backend/
│   ├── app/
│   │   ├── controllers/            # Lógica de negocio y controladores de cada módulo
│   │   │   ├── auth_controller.py      # Login, registro protegido y bloqueo por intentos fallidos
│   │   │   ├── catalog_controller.py   # Actualización de catálogos CURP.xlsx y STPS.xlsx
│   │   │   ├── document_controller.py  # Extracción PDF, generación Word/Excel y empaquetado ZIP
│   │   │   ├── event_controller.py     # Gestión de eventos, fases, trabajadores y calificaciones
│   │   │   ├── excel_controller.py     # Lectura previa de eventos desde archivos Excel
│   │   │   ├── stats_controller.py     # Consultas SQL de indicadores y métricas del Dashboard
│   │   │   ├── stps_controller.py      # Exportación de formatos STPS.xlsm y SCPM-07.xlsx
│   │   │   └── template_controller.py  # Conversión de etiquetas [CAMPO] a Jinja2 en plantillas
│   │   ├── models/                 # Modelos ORM de SQLAlchemy
│   │   │   ├── course.py               # Modelo Curso (tabla 'cursos')
│   │   │   ├── curp.py                 # Modelo Curp (tabla 'curps')
│   │   │   ├── history.py              # Modelo HistorialCapacitacion (tabla 'historial_capacitacion')
│   │   │   └── user.py                 # Modelo User (tabla 'usuarios')
│   │   ├── routes/                 # Definición de Blueprints y middleware de autenticación JWT
│   │   ├── schemas/                # Esquemas de serialización Marshmallow
│   │   ├── utils/                  # Utilidades de seguridad y manejo de tokens
│   │   │   ├── jwt_utils.py            # Generación y decodificación de tokens JWT
│   │   │   └── security.py             # Validación de rutas, sandbox Jinja2 y bloqueos de eventos
│   │   ├── config.py               # Configuración central y gestión de SECRET_KEY
│   │   └── __init__.py             # Factoría create_app() e inicialización de base de datos
│   ├── catalogos/                  # Catálogos base (CURP.xlsx, STPS.xlsm y catálogos STPS 01-10)
│   ├── templates/                  # Plantillas institucionales (.docx, .xlsx y .xlsm)
│   ├── tests/
│   │   └── test_app.py             # Pruebas unitarias del backend con Pytest
│   ├── create_user.py              # Script auxiliar para crear el usuario admin manualmente
│   ├── requirements.txt            # Dependencias de Python
│   ├── run.py                      # Punto de entrada WSGI / desarrollo local
│   └── Dockerfile                  # Imagen Docker del backend (Python 3.9 + Gunicorn)
├── frontend/
│   ├── public/                     # Logotipos institucionales y recursos estáticos
│   ├── src/
│   │   ├── pages/                  # Vistas principales de la aplicación
│   │   │   ├── Catalogos.tsx           # Carga de catálogos CURP y STPS
│   │   │   ├── Dashboard.tsx           # Panel estadístico, gráficas y exportación CSV/PNG
│   │   │   ├── DetalleEvento.tsx       # Gestión de trabajadores, bajas, SCPM-07 y STPS por evento
│   │   │   ├── Generador.tsx           # Flujo principal de 3 pasos para generar expedientes
│   │   │   ├── Historial.tsx           # Tabla histórica de eventos y descarga de ZIP
│   │   │   ├── Login.tsx               # Inicio de sesión
│   │   │   └── Plantillas.tsx          # Subida de plantillas y guía de etiquetas disponibles
│   │   ├── services/
│   │   │   └── api.ts                  # Instancia Axios configurada hacia el backend
│   │   ├── App.css                 # Estilos institucionales de la interfaz
│   │   ├── App.test.js             # Pruebas de integración de navegación en React
│   │   ├── App.tsx                 # Enrutador principal, sesión e interceptor JWT
│   │   └── index.tsx               # Punto de montaje de React
│   ├── index.html                  # Plantilla HTML raíz para Vite
│   ├── package.json                # Dependencias y scripts de Node.js
│   ├── vite.config.js              # Configuración de compilación con Vite
│   └── Dockerfile                  # Construcción multi-etapa (Node 20 Alpine -> Nginx Alpine)
├── .env.example                    # Plantilla de variables de entorno
├── .gitignore                      # Exclusión de cachés, entornos virtuales y archivos temporales
├── docker-compose.yml              # Orquestación de contenedores Docker
├── init.sql                        # Script inicial de selección de esquema en MySQL
└── manual_de_usuario.md            # Manual operativo paso a paso para usuarios finales
```

---

## Guía para Futuros Practicantes

Esta sección resume los puntos técnicos clave para quienes den mantenimiento o extiendan el proyecto:

1. **Arquitectura Backend (`backend/app/`):**
   * Toda ruta nueva bajo `/api/*` queda protegida automáticamente por el hook `@app.before_request` (`check_token`) ubicado en `backend/app/routes/init_routes.py`.
   * Cuando crees o modifiques un controlador que escriba archivos de un evento en disco, utiliza siempre `event_dir(id_evento, create=True)` de `backend/app/utils/security.py` en lugar de concatenar rutas manualmente, para prevenir vulnerabilidades de *Path Traversal*.
   * Para devolver errores de servidor (500), utiliza `error_response(mensaje, codigo, excepcion)` de `security.py`, de modo que el detalle técnico quede registrado en los logs del contenedor sin exponerse al cliente.
2. **Cómo funciona el Motor de Plantillas:**
   * **Word (`.docx`):** Se procesa con `docxtpl` (`DocxTemplate`). Las plantillas grupales tienen acceso a la lista `lista_participantes` para iterar filas en tablas de Word, además de las variables generales del curso.
   * **Excel (`.xlsx` / `.xlsm`):** Se procesa con `openpyxl` y `render_template_string` (entorno Jinja2 en sandbox). Casos especiales:
     * `SCPM-07.xlsx`: Agrupa a los participantes activos de 5 en 5 en las columnas `I` a `M` (índices 9 a 13), clonando la hoja base para cada bloque de 5 trabajadores (ver `stps_controller.py` y `document_controller.py`).
     * `SIRCE_Automatizado.xlsm`: Inyecta directamente los registros en las hojas `BD_TRABAJADORES` y `BD_CURSOS` preservando las macros VBA (`keep_vba=True`) y actualizando el rango de las tablas `ListObject`.
   * **Nuevas etiquetas:** Si necesitas agregar una nueva etiqueta como `[MI_NUEVA_ETIQUETA]`, regístrala en el diccionario `tag_mapping` de `backend/app/controllers/template_controller.py`, agrégala al contexto `ctx_ind` / `ctx_grp` en `document_controller.py`, y añádela al arreglo visual de `frontend/src/pages/Plantillas.tsx`.
3. **Ejecución de Pruebas:**
   * **Backend:** Desde la carpeta `backend/`, ejecuta `pytest tests/`.
   * **Frontend:** Desde la carpeta `frontend/`, ejecuta `npm test -- --watchAll=false`.
