# Usa una imagen oficial de Python ligera
FROM python:3.10-slim

# Evita que Python genere archivos .pyc y fuerza la salida por consola
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia las dependencias e instálalas
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia el resto del código del proyecto
COPY . /app/