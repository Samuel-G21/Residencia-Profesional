# 1. Usar una imagen oficial de Python ligera
FROM python:3.9-slim

# 2. Instalar LibreOffice para la conversión de Word a PDF
RUN apt-get update && apt-get install -y libreoffice --no-install-recommends

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar el archivo de dependencias y ejecutarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código del backend
COPY . .

# 6. Exponer el puerto que usará Flask
EXPOSE 5000

# 7. Comando por defecto para arrancar la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]