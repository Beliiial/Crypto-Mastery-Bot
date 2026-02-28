from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    BOT_TOKEN: str
    CRYPTO_PAY_TOKEN: str
    ADMIN_IDS: str
    DATABASE_URL: str
    CHANNEL_ID: int
    STUDENT_CHAT_ID: int = 0
    TRIAL_FILE_ID: str = "DEFAULT_FILE_ID"

    @property
    def admins(self) -> List[int]:
        return [int(admin_id.strip()) for admin_id in self.ADMIN_IDS.split(",") if admin_id.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

config = Settings()
