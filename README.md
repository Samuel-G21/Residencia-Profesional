# Sistema de Generación de Documentos de Capacitación (PEMEX / TECNM)

![Arquitectura](https://img.shields.io/badge/Architecture-Docker-blue?style=for-the-badge&logo=docker)
![Backend](https://img.shields.io/badge/Backend-Flask_|_Python-green?style=for-the-badge&logo=python)
![Frontend](https://img.shields.io/badge/Frontend-React_|_Vite-61DAFB?style=for-the-badge&logo=react)
![Base de Datos](https://img.shields.io/badge/Database-MySQL-orange?style=for-the-badge&logo=mysql)

Un sistema integral diseñado para automatizar y agilizar el proceso de gestión de expedientes y generación de documentos de capacitación institucional. Esta plataforma reduce significativamente el tiempo de procesamiento manual al extraer información directamente de archivos PDF y generar formatos oficiales (.docx y .xlsx) listos para impresión o firma.

---

## ✨ Características Principales

* **Extracción Inteligente:** Integración con *Gotenberg* y *PDFPlumber* para extraer listas de asistencia directamente desde archivos PDF.
* **Procesamiento de Plantillas:** Generación automatizada de formatos individuales y grupales (SCPM-04, SCPM-05, SCPM-06, SCPM-07, DC-3, FVC, etc.) utilizando `docxtpl` y `openpyxl`.
* **Cruce de Datos:** Coincidencia de trabajadores con catálogos internos para autocompletado de información crítica (CURP, Niveles, Departamentos).
* **Flujo Asistido (Wizard):** Interfaz gráfica intuitiva que guía al usuario paso a paso (Registro -> Extracción -> Integración -> Descarga).
* **Dashboard Estadístico:** Monitoreo en tiempo real de métricas, trabajadores únicos capacitados, cursos impartidos y gráficas de distribución de fases.
* **Descarga Empaquetada:** Consolidación de todos los documentos generados de un curso en un solo archivo `.zip` para facilitar la gestión documental.

---

## 🛠️ Stack Tecnológico

**Frontend:**
* React.js
* Vite (Bundler)
* CSS Moderno (Responsive)

**Backend:**
* Python 3.9+
* Flask (API REST)
* Pandas / openpyxl (Procesamiento de datos y Excel)
* docxtpl (Inyección de datos en plantillas de Word)

**Infraestructura & Servicios:**
* Docker & Docker Compose
* MySQL 8.0 (Base de datos relacional)
* Gotenberg (Microservicio para manipulación de PDFs)

---

## 🚀 Requisitos Previos

Asegúrate de tener instalado lo siguiente en tu sistema antes de comenzar:

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (o Docker Engine)
* [Docker Compose](https://docs.docker.com/compose/install/)
* Git (Opcional, para control de versiones)

---

## ⚙️ Instalación y Despliegue

El proyecto está completamente dockerizado para facilitar su despliegue sin depender del entorno local.

1. **Clonar/Abrir el repositorio:**
   Ve al directorio raíz del proyecto donde se encuentra el archivo `docker-compose.yml`.

2. **Levantar los servicios:**
   Abre una terminal en la ruta del proyecto y ejecuta:
   ```bash
   docker-compose up -d --build
   ```
   Esto descargará las imágenes necesarias, construirá el frontend y backend, y levantará 4 contenedores:
   * `pemex_frontend` (Puerto 3000)
   * `pemex_backend` (Puerto 5000)
   * `pemex_gotenberg` (Puerto 3001)
   * `pemex_mysql` (Puerto 3307)

3. **Acceder a la aplicación:**
   Una vez que los contenedores estén corriendo, abre tu navegador web y visita:
   👉 **http://localhost:3000**

---

## 📖 Guía Rápida de Uso

1. **Catálogos:** Primero, asegúrate de cargar tu catálogo base (Excel) en la sección **"Cargar Catálogos"**. Esto nutrirá a la base de datos con las CURPs y datos maestros.
2. **Generación de Expedientes:** 
   * Ve a **"Gestión de Expedientes"**.
   * **Paso 1:** Sube el PDF de la lista de asistencia. El sistema te devolverá un Excel extraído.
   * **Paso 2:** Llena la información del evento, selecciona las plantillas a generar (ej. *SCPM-05*, *SCPM-07*) y sube el Excel del Paso 1.
   * **Paso 3:** Haz clic en generar y espera a que el sistema procese todos los documentos. Finalmente, descarga tu `.zip` consolidado.
3. **Historial:** Revisa la sección **"Historial de Eventos"** para consultar eventos pasados, volver a descargar sus documentos o eliminarlos.

---

## 📂 Estructura del Proyecto

```text
📁 Proyecto
├── 📁 backend/              # API Flask en Python
│   ├── app.py               # Controlador principal
│   ├── requirements.txt     # Dependencias de Python
│   └── 📁 templates/        # Plantillas base (.docx, .xlsx)
├── 📁 frontend/             # Código fuente de React
│   ├── 📁 src/              # Componentes, vistas y estilos
│   └── package.json         # Dependencias de Node
├── docker-compose.yml       # Orquestador de contenedores
└── init.sql                 # Script de inicialización de Base de Datos
```

---

*Desarrollado para la agilización de procesos administrativos de capacitación.*
