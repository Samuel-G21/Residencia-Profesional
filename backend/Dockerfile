# 1. Usar una imagen oficial de Python ligera
FROM python:3.9-slim

# 2. Instalar LibreOffice para la conversión de Word a PDF y dependencias del sistema
RUN apt-get update && apt-get install -y \
    libreoffice \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar el archivo de dependencias y ejecutarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código del backend (app.py, templates, etc.)
COPY . .

# 6. Crear las carpetas de outputs por si no existen
RUN mkdir -p outputs

# 7. Exponer el puerto que usará Flask
EXPOSE 5000

# 8. Comando por defecto para arrancar la aplicación
CMD ["python", "app.py"]