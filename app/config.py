from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_environment(self):
        env_name = (self.ENVIRONMENT or "").lower()
        secret = self.SECRET_KEY or ""
        if env_name == "production":
            if not self.ADMIN_USERNAME:
                raise ValueError("ADMIN_USERNAME must be configured in production.")
            if not self.ADMIN_PASSWORD:
                raise ValueError("ADMIN_PASSWORD must be configured in production.")
            if "dev-secret-key-change-me" in secret.lower() or "change-me" in secret.lower() or secret == "":
                raise ValueError("SECRET_KEY must be set to a secure value in production.")
            if self.DATABASE_URL.startswith("sqlite"):
                raise ValueError("Production environment must use a real database URL, not SQLite.")
        return self


settings = Settings()