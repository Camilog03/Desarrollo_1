# 1. Usar una imagen oficial de Python ligera
FROM python:3.11-slim

# 2. Crear una carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el archivo de requerimientos e instalar las librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el resto del código del backend
COPY . .

# 5. Comando para arrancar FastAPI con recarga automática
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
