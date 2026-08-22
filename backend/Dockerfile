# 1.- Uso de la imagen oficial de Python "slim"
FROM python:3.9-slim

# 2.- Establecemos el directorio de trabajo en el contendor
WORKDIR /app

# 3.- Copiar el archivo "requirements.txt" y ejecutarlo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4.- Copia el el resto del backend
COPY . .

# 5.- Abrir el puerto que usara el backend
EXPOSE 5000

# 6.- Comando de arranque inicial
CMD ["flask", "run", "--host=0.0.0.0"]