from sqlalchemy.orm import Session
from app.db.depends import get_db_session
from app.schemas.schemas import ClickIn
from app.db.models import ClickModel
from datetime import datetime
import socket

class RepositoryClick:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def salve_click(self, click: ClickIn,short_link):
        click_model = ClickModel(
            link_short_id= short_link,
            user_agent=click.user_agent,
            ip=click.ip,
            localization=click.localization,
            created_at=datetime.utcnow()
        )
        self.db_session.add(click_model)
        self.db_session.commit()
        self.db_session.refresh(click_model)

        return click_model

    def get_local_ip(self):
        self.hostname = socket.gethostname()
        self.local_ip = socket.gethostbyname(self.hostname)
        return self.local_ip