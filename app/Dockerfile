# app/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copiez les dépendances
COPY ../requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste du code
COPY . /app/

# Copier le fichier alembic.ini et le répertoire alembic
COPY ../alembic.ini /app/alembic.ini
COPY ../alembic /app/alembic

# Exécutez les migrations Alembic puis démarrez FastAPI
CMD ["sh", "-c", "alembic -c /app/alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8008"]
