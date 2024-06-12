from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="Core/.env")
    DB_URL: str
    DB_URL_NOTES: str
    SECRET_KEY: str
    ALGORITHM: str
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    USER_URI: str

settings = Settings()


