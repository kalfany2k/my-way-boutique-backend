from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_access_key: str
    aws_secret_key: str
    aws_region: str
    aws_bucket_name: str

    class Config:
        env_file = ".aws"

settings = Settings()