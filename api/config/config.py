from pydantic import BaseSettings
from enum import Enum
from functools import lru_cache

class Profile(str, Enum):
    STAGING = "staging"

class ProfileSetting(BaseSettings):
    profile: Profile

    def get_settings(self):
        return Settings(_env_file="api/environments/.env" + "." + self.profile.lower()) # type: ignore

    class Config:
        # env_file = "../.env"
        env_file = "api/environments/.env"
        env_file_encoding = "utf-8"


class Settings(BaseSettings):
    DB_URL: str
    OPENAI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SERPER_API_KEY: str

    class Config:
        case_sensitive = True
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    profile = ProfileSetting() # type: ignore
    return profile.get_settings()