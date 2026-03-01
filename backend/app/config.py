from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://scoreapp:scoreapp123@db:5432/scoreapp"
    jwt_secret: str = "change-this-to-a-random-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7
    admin_username: str = "admin"
    admin_password: str = "admin123"

    class Config:
        env_file = ".env"


settings = Settings()
