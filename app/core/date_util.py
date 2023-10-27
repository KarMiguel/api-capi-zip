from datetime import datetime
from app.core.settings import get_settings

settings = get_settings()


def current_time() -> datetime:
    return datetime.now(tz=settings.TZ_DEFAULT)  # type: ignore
