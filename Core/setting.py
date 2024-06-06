from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="Core/.env")
    DB_URL: str

settings = Settings()
