import boto3
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
        message_text: str,
        message_html: str = None,
):
    try:
        message_body = {"Text": {"Data": message_text}}
        if message_html:
            message_body["Html"] = {"Data": message_html}

        response = ses.send_email(
            Source="extremesurvivalboys@gmail.com",
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject},
                "Body": message_body,
            },
        )
        return {"message": "Email sent successfully", "message_id": response["MessageId"]}
    except Exception as e:
        return {"error": str(e)}