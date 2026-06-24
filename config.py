from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    )
    API_KEY: str = "secret_key1234"
    API_KEY_NAME: str = "X-API-Key"

    @property
    def db_url(self) -> str:
        return self.DATABASE_URL


settings = Settings()
