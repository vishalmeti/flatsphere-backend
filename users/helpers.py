import boto3
from botocore.exceptions import NoCredentialsError
from decouple import config

def upload_to_s3(file_name, file, bucket_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY')
    )
    
    try:
        s3.upload_fileobj(file, bucket_name, file_name)
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        return file_url, "File uploaded successfully"
    except NoCredentialsError:
        return None, "Credentials not available"
    except Exception as e:
        return None, str(e)
