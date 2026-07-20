from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cbam"
    cors_origins: str = "http://localhost:3000"
    report_storage_path: str = "./reports"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
