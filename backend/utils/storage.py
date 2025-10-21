import io

from minio import Minio
from utils.settings import AppSettings


class MinioClient:
    def __init__(self, client: Minio, bucket: str):
        self.client = client
        self.bucket = bucket
        found = self.client.bucket_exists(bucket)
        if not found:
            self.client.make_bucket(bucket)

    @classmethod
    def from_env(cls, settings: AppSettings):
        print("creating minio client", flush=True)
        m = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False,
        )
        return cls(m, settings.MINIO_BUCKET)

    def put_file(
        self, key: str, data: bytes, content_type: str = "application/octet-stream"
    ) -> None:
        self.client.put_object(
            self.bucket,
            key,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
