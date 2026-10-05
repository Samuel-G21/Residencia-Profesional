# Manual de Usuario: Sistema de Automatización Documental y Análisis Estadístico

## 1. Introducción
Bienvenido al **Sistema de Automatización Documental y Análisis Estadístico**. Esta herramienta web fue diseñada para optimizar y agilizar la gestión de los cursos de capacitación en PEMEX. 

Su propósito principal es automatizar las tareas repetitivas: el sistema es capaz de extraer información de un documento PDF, procesar esos datos a través de hojas de cálculo, y generar de manera masiva todos los formatos operativos necesarios para tus cursos. Además, te proporciona un panel visual (Dashboard) para analizar estadísticamente el estado de las capacitaciones y sus participantes de forma clara y rápida.

## 2. Requisitos Previos
Antes de comenzar a utilizar el sistema, asegúrate de contar con lo siguiente:
* **Credenciales de acceso:** Un usuario y contraseña vigentes.
* **Archivo fuente:** El documento PDF original con la información del curso de capacitación que deseas procesar.
* **Software básico:** Un navegador web actualizado y un programa capaz de abrir archivos comprimidos (tipo `.zip`) y hojas de cálculo (tipo `.xlsx`).

---

## 3. Guía Paso a Paso de Uso

### Fase A: Ingreso al Sistema
1. Abre tu navegador web y dirígete a la dirección del portal del sistema.
2. En la pantalla principal, localiza los campos de inicio de sesión.
3. Introduce tu **Usuario** y tu **Contraseña**.
4. Haz clic en el botón de ingresar para acceder.

### Fase B: Extracción de Datos
Para evitar que escribas la información a mano, el sistema la extraerá por ti:
1. Una vez dentro de la **Página Principal**, busca la sección dedicada a la carga del archivo inicial.
2. Sube el documento **PDF** del curso.
3. El sistema leerá el PDF de forma automática y descargará un archivo de Excel (`.xlsx`) en tu computadora. Este archivo contiene la información extraída y pre-organizada.

> [!IMPORTANT]  
> **Paso de Validación:** Abre el archivo Excel que acabas de descargar y revísalo rápidamente. Asegúrate de que los nombres de los participantes, fechas e información del curso se hayan extraído correctamente y no haya errores de dedo o datos faltantes. Si encuentras algún error, corrígelo en el Excel y guárdalo antes de pasar al siguiente paso.

### Fase C: Generación Masiva de Formatos
Una vez que el Excel está validado, generaremos los documentos finales:
1. Regresa a la **Página Principal** del sistema.
2. En la sección correspondiente, sube el archivo Excel (`.xlsx`) que el sistema te entregó en el paso anterior (y que ya validaste).
3. Haz clic en el botón de **Generar Documentos**.
4. El sistema procesará la información y automáticamente descargará un archivo comprimido `.zip` en tu computadora.
5. Extrae el contenido del `.zip`. En su interior encontrarás los formatos listos para su uso:
   * 1. Cédula registro actualizado 2025 COMBINADA
   * 2. Constancias de Habilidades
   * DC-3 2026 COMBINADA
   * 5. Carta Compromiso Instructor 2026 COMBINADA
   * FVC
   * Informe Técnico Instructor 2025
   * SCPM-03
   * SCPM-04 COMBINADA
   * SCPM-04
   * SCPM-05 2025
   * SCPM-05A
   * SCPM-06 COMBINADA
   * SCPM-07

### Fase D: Monitoreo y Análisis Estadístico
Para tener una visión global de tus operaciones:
1. En el menú del sistema, dirígete a la sección **Dashboard Estadístico**.
2. Aquí podrás interactuar con gráficos de barras y de pastel que se actualizan según los datos del sistema. 
3. Utiliza estas gráficas para visualizar rápidamente:
   * **Estado de los cursos:** Cursos en progreso, finalizados y cancelados.
   * **Volumen:** Cantidad total de participantes.
   * **Demografía:** Género de los participantes.
   * **Retención:** Participantes que se dieron de baja.

---

## 4. Solución de Problemas (FAQ)

**1. El sistema marca error o genera los formatos en blanco después de subir el Excel.**
* **Causa común:** El archivo Excel contiene errores, información desfasada, nombres mal escritos o celdas importantes vacías generadas durante la extracción del PDF.
* **Solución:** Abre el archivo `.xlsx`, verifica que toda la información esté en las columnas correctas y no haya caracteres extraños o errores tipográficos. Guarda los cambios e intenta subir el archivo nuevamente.

**2. No puedo ingresar al sistema, me indica que mis datos son incorrectos.**
* **Causa común:** El usuario o la contraseña tienen un error de escritura.
* **Solución:** Revisa que la tecla de *Bloqueo de Mayúsculas (Caps Lock)* no esté activada por accidente, ya que las contraseñas son sensibles a mayúsculas y minúsculas. Si el problema persiste, solicita al administrador que restablezca tu contraseña.

**3. El archivo `.zip` con los formatos no se descarga automáticamente.**
* **Causa común:** El navegador web bloqueó la descarga porque la consideró una "ventana emergente" o el proceso está tomando tiempo.
* **Solución:** Revisa la barra de direcciones de tu navegador (en la parte superior derecha); si ves un ícono con una pequeña "X" roja, haz clic en él y selecciona "Permitir descargas/ventanas emergentes de este sitio". Además, ten un poco de paciencia si el curso tiene muchos participantes, el sistema puede tardar unos segundos en compilar todos los documentos.
