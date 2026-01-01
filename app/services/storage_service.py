import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile, HTTPException
from app.core.config import settings

class StorageService:
    @staticmethod
    def upload_to_s3(file: UploadFile, filename: str) -> str:
        """Upload file to S3 and return the URL."""
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            
            # Upload file
            s3_client.upload_fileobj(file.file, settings.s3_bucket_name, filename)
            
            # Generate URL
            url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{filename}"
            return url
        except NoCredentialsError:
            raise HTTPException(status_code=500, detail="AWS credentials not available")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
