# app/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Définir PYTHONPATH pour inclure /app
ENV PYTHONPATH=/app

# Copier les dépendances en premier
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le reste du code de l'application
COPY ./app /app/

# Copier le fichier alembic.ini et le répertoire alembic
COPY ./alembic.ini /app/alembic.ini
COPY ./alembic /app/alembic

# Exécuter les migrations Alembic puis démarrer FastAPI
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8008
