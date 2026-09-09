FROM python:3.9-slim

WORKDIR /app

# Instalar gunicorn y dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn requests

COPY . .

RUN mkdir -p outputs

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]