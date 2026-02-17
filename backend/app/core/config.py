from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str
    azure_key_vault_url: str
    admin_api_key: str
    azure_storage_connection_string: str | None = None
    
    collector_interval_minutes: int = 15
    collector_max_concurrency: int = 10
    log_level: str = "INFO"
    
    app_version: str = "0.1.0"


settings = Settings()
