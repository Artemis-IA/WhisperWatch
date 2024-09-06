FROM postgres:13

# Définir les variables d'environnement
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=veille_mlops

# Copier le script d'initialisation dans le répertoire de démarrage de PostgreSQL
COPY init.sql /docker-entrypoint-initdb.d/

# Exposer le port PostgreSQL
EXPOSE 5432
