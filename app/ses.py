import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from .aws_config import settings

ses = boto3.client(
    "ses", 
    aws_access_key_id=settings.aws_access_key,
    aws_secret_access_key=settings.aws_secret_key,
    region_name=settings.aws_region
)

def send_email_via_ses(
        recipient: str,
        subject: str,
        message_text: str = None,
        message_html: str = None,
):
    try:
        response = ses.send_email(
            Source="extremesurvivalboys@gmail.com",
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {
                    "Data": subject
                    },
                "Body": {
                    "Text": {
                        "Data": message_text
                    },
                    "Html": {
                        "Data": message_html
                    } 
                }
            },
        )
        print(f'Seding email to {recipient}...')
        return response
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e.response['Error']['Message']}")