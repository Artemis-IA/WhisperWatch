# app/db/s3.py
import boto3
from botocore.exceptions import NoCredentialsError
import logging
from core.config import settings

class S3:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=settings.MINIO_ENDPOINT,  # Spécifiez l'URL de MinIO
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

        # Créer le bucket si ce n'est pas déjà fait
        self._create_bucket()

    def _create_bucket(self):
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
            logging.info(f"Bucket {self.bucket_name} already exists.")
        except self.s3.exceptions.NoSuchBucket:
            self.s3.create_bucket(Bucket=self.bucket_name)
            logging.info(f"Bucket {self.bucket_name} created.")

    def upload_file(self, file_path, s3_key):
        try:
            self.s3.upload_file(file_path, self.bucket_name, s3_key)
            logging.info(f"File {file_path} uploaded to bucket {self.bucket_name} as {s3_key}.")
            return f"{settings.MINIO_ENDPOINT}/{self.bucket_name}/{s3_key}"
        except FileNotFoundError:
            raise Exception("The file was not found")
        except NoCredentialsError:
            raise Exception("Credentials not available")

    def get_file_url(self, object_name):
        try:
            url = self.s3.generate_presigned_url('get_object', Params={
                'Bucket': self.bucket_name,
                'Key': object_name
            }, ExpiresIn=3600)  # URL expirant après 1 heure
            logging.info(f"Generated URL for object {object_name}: {url}")
            return url
        except Exception as e:
            logging.error(f"Error generating presigned URL: {e}")
            raise
