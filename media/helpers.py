import boto3
from botocore.exceptions import NoCredentialsError
from botocore.config import Config
from decouple import config


class S3Helper:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
            region_name=config("AWS_S3_REGION_NAME"),
            config=Config(signature_version="s3v4"),
        )

    def upload_to_s3(self, file_name, file, bucket_name):
        try:
            self.s3.upload_fileobj(file, bucket_name, file_name)
            # file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
            return file_name, "File uploaded successfully"
        except NoCredentialsError:
            return False, "Credentials not available"
        except Exception as e:
            return False, str(e)

    def get_presigned_url(self, file_name):
        try:
            response = self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": config("AWS_STORAGE_BUCKET_NAME"), "Key": file_name},
                ExpiresIn=3600,
            )
            return response
        except Exception as e:
            return str(e)
