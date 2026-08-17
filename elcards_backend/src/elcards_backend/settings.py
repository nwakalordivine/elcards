from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")
    database_url: str
    secret: str
    algorithm: str
    resend_apikey: str
    my_email: str
    reset_code_timer: int
    auth_reset_code_lenth: int = 4
    redis_url: str
    redis_token: str
    ratelimit_hour: int = 1
    reset_max_attempts: int = 3
    access_token_expire_minutes: int = 60
    change_password_timer: int = 5


settings = Settings()