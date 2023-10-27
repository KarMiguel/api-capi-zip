from datetime import tzinfo
from functools import lru_cache
from pydantic import ValidationError, validator
from dateutil import tz
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    TZ_DEFAULT: tzinfo | str = "UTC"

    @validator("TZ_DEFAULT")
    def validate_timezone(cls, v: str) -> tzinfo:
        current_timezone = tz.gettz(v)
        if current_timezone is None:
            raise ValueError("Invalid timezone")
        return current_timezone


@lru_cache  # https://fastapi.tiangolo.com/advanced/settings/#settings-in-a-dependency
def get_settings() -> Settings:
    try:
        return Settings()  # type: ignore
    except ValidationError as ve:
        details = [f'{error["loc"]}: {error["msg"]}' for error in ve.errors()]
        msg = "Failed to load settings:\n" + "\n".join(details)
        raise RuntimeError(msg) from ve
