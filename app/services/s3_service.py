# app/services/s3_service.py
import boto3
from botocore.exceptions import NoCredentialsError
from app.core.config import settings

class S3Service:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=settings.MINIO_ENDPOINT,  # Spécifiez l'URL de MinIO
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    def upload_file(self, file_path, s3_key):
        try:
            # Créez un bucket si ce n'est pas déjà fait
            self.s3.create_bucket(Bucket=self.bucket_name)
        except self.s3.exceptions.BucketAlreadyOwnedByYou:
            pass  # Le bucket existe déjà

        try:
            # Téléchargement du fichier sur MinIO
            self.s3.upload_file(file_path, self.bucket_name, s3_key)
            return f"{settings.MINIO_ENDPOINT}/{self.bucket_name}/{s3_key}"
        except FileNotFoundError:
            raise Exception("The file was not found")
        except NoCredentialsError:
            raise Exception("Credentials not available")
