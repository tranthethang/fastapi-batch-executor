from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Gemini API Configuration
    GEMINI_API_KEY: str
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-southeast-1"
    S3_BUCKET_NAME: str
    
    # Execution Control
    CONCURRENCY_LIMIT: int = 3 # Number of concurrent Gemini requests
    APP_PORT: int = 60062
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()