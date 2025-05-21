from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@db:5432/mydatabase"
    secret_key: str = "your-super-secret-key" # Change this in production
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    documents_upload_path: str = "uploaded_documents" # Directory to save uploaded files

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
# Roo temp change 3