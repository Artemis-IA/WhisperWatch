Voici un fichier `README.md` complet pour votre projet **WhisperWatch** :

```md
# WhisperWatch

**WhisperWatch** est un projet innovant de veille technique qui permet de scraper des vidéos YouTube, de transcrire leur contenu audio en texte, et de stocker les métadonnées ainsi que les transcriptions dans une base de données. Il se concentre sur des sujets techniques tels que le Cloud et le MLOps, facilitant ainsi la veille technologique à partir de vidéos YouTube.

## Fonctionnalités

- **Scraping de vidéos YouTube** : Extraction des métadonnées des vidéos YouTube en fonction de critères définis.
- **Transcription audio en texte** : Utilisation du modèle **Whisper** pour transcrire l'audio des vidéos en texte.
- **Stockage audio et texte** : Sauvegarde des fichiers audio dans MinIO et des transcriptions dans une base de données SQL.
- **Support des métadonnées YouTube** : Stockage des métadonnées pertinentes des vidéos (titre, description, URL, date de publication).
- **Veille automatisée** : Utilisation de tâches **Celery** pour automatiser la récupération et la transcription de nouvelles vidéos YouTube.

## Pré-requis

- **Docker** et **Docker Compose** installés
- **Python 3.10+**
- **PostgreSQL** pour la base de données SQL
- **MinIO** comme stockage d'objets (équivalent à S3)
- **Redis** pour le broker Celery
- **yt-dlp** pour télécharger l'audio des vidéos YouTube

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/username/whisperwatch.git
cd whisperwatch
```

### 2. Configuration de l'environnement

Renommer le fichier `.env.example` en `.env` et configurer les variables d'environnement :

```bash
cp db/.env.example db/.env
```

Dans le fichier `.env`, configurer les paramètres suivants :

```bash
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=bucket

POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=db
POSTGRES_HOST=host
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0
```

### 3. Lancer les services avec Docker Compose

Lancer la base de données PostgreSQL, MinIO et Redis à l'aide de Docker Compose :

```bash
cd db
docker compose up --build -d
```

### 4. Installer les dépendances Python

Créer un environnement virtuel et installer les dépendances :

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Initialiser la base de données

Effectuer les migrations avec **Alembic** pour créer les tables `users` et `videos` dans la base de données :

```bash
alembic upgrade head
```

### 6. Lancer l'application

Lancer l'API FastAPI :

```bash
uvicorn app.main:app --reload
```

L'API sera accessible à l'adresse suivante : [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Utilisation

### Endpoints disponibles

- `GET /api/`: Récupérer une liste de vidéos (avec pagination).
- `POST /api/`: Créer une nouvelle entrée vidéo (scraping et transcription automatique).
- `GET /api/{video_id}`: Récupérer les détails d'une vidéo spécifique.
- `PUT /api/{video_id}`: Mettre à jour les détails d'une vidéo.
- `DELETE /api/{video_id}`: Supprimer une vidéo de la base de données.

### Exemple d'appel API

Pour ajouter une nouvelle vidéo :

```bash
curl -X POST "http://127.0.0.1:8000/api/" \
     -H "Content-Type: application/json" \
     -d '{
           "youtube_id": "a_qTAJMXk9A",
           "title": "Introduction to MLOps",
           "description": "A comprehensive guide to MLOps.",
           "published_at": "2024-09-05T12:00:00",
           "video_url": "https://www.youtube.com/watch?v=a_qTAJMXk9A"
         }'
```

### Gestion des transcriptions

Le service de transcription est géré par **Whisper**, qui convertit l'audio des vidéos YouTube en texte. Ces transcriptions sont ensuite stockées dans la base de données et peuvent être récupérées via l'API.

## Structure du Projet

```
.
├── app/
│   ├── api/
│   │   └── video_api.py       # Endpoints pour les vidéos
│   ├── core/
│   │   └── config.py          # Configuration de l'application
│   ├── crud/
│   │   └── crud_video.py      # Logique CRUD pour les vidéos
│   ├── db/
│   │   └── database.py        # Configuration de la base de données
│   ├── models/
│   │   └── video.py           # Modèle SQLAlchemy pour les vidéos
│   ├── schemas/
│   │   └── video.py           # Schémas Pydantic pour les vidéos
│   ├── services/
│   │   ├── download_service.py # Téléchargement de l'audio
│   │   ├── transcription_service.py # Transcription des vidéos
│   │   ├── s3_service.py      # Gestion du stockage MinIO
│   └── main.py                # Point d'entrée de l'API
├── db/
│   ├── docker-compose.yml      # Docker Compose pour PostgreSQL, Redis et MinIO
│   └── .env.example            # Variables d'environnement
├── alembic/
│   └── versions/               # Migrations Alembic
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation du projet
```

## Tâches Celery

L'automatisation de la veille technique est gérée via **Celery**. Les tâches Celery exécutent régulièrement des recherches et des transcriptions automatiques sur des sujets définis dans le cadre de la veille.

### Lancer Celery Worker

```bash
celery -A app.worker worker --loglevel=info
```

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d’informations.
``