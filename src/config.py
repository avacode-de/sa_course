from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_aiosqlite(self):
        # postgresql+asyncpg://postgres:postgres@localhost:5432/sa
        return f"sqlite+aiosqlite:///sa.db"

    @property
    def DATABASE_URL_pysqlite(self):
        # DSN
        # postgresql+psycopg://postgres:postgres@localhost:5432/sa
        return f"sqlite+pysqlite:///sa.db"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()