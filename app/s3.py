import uuid
import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile
from .aws_config import settings
from fastapi import status
from sqlalchemy.orm import Session

BUCKET_NAME = settings.aws_bucket_name

s3_client = boto3.resource(
    's3',
    aws_access_key_id=settings.aws_access_key,
    aws_secret_access_key=settings.aws_secret_key,
    region_name=settings.aws_region
)
bucket = s3_client.Bucket(BUCKET_NAME)

async def upload_file_to_s3(file: UploadFile, item_type: str) -> str:
    try:
        extension = file.filename.split('.')[-1]
        filename = f'{item_type}/{uuid.uuid4()}.{extension}'
        contents = await file.read()
        bucket.put_object(
            Key=filename,
            Body=contents,
            ContentType=file.content_type
        )
        return f'https://{BUCKET_NAME}.s3.amazonaws.com/{filename}'
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_file_from_s3(file: str, folder: str, db: Session):
    try:
        print(f'Deleting file... {folder}/{file}')
        bucket.delete_objects(Delete={'Objects': [{'Key': f'{folder}/{file}'}]})
    except ClientError as e:
        db.rollback()
        raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           detail=f"Error deleting S3 objects: {str(e)}"
        )