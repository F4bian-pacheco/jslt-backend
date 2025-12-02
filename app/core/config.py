from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "JSLT Playground API"
    version: str = "1.0.0"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # CORS settings
    backend_cors_origins: list[str] = [
        "*"
    ]

    class Config:
        env_file = ".env"


settings = Settings()
