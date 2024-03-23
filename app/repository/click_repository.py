from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from app.db.depends import get_db_session
from app.repository.link_repository import RepositoryLink
from app.schemas.schemas import ClickIn
from app.db.models import ClickModel,LinkShortModel
from datetime import datetime
from sqlalchemy.sql.expression import select
import socket

class RepositoryClick:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def salve_click(self, click: ClickIn, short_link: str):
        link_short = RepositoryLink(db_session=self.db_session).obter_short_link_generate(short_link)
        if not link_short:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found.")
        
        click_model = ClickModel(
            link_short_id=link_short.short_link,
            user_agent=click.user_agent,
            ip=click.ip,
            localization=click.localization,
            created_at =  datetime.utcnow()
        )
        self.db_session.add(click_model)
        self.db_session.commit()
        self.db_session.refresh(click_model)

        return click_model


    def get_local_ip():
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
        
    def list_all_click_link(self, short_link: str):
        return self.db_session.query(ClickModel).filter(ClickModel.link_short_id == short_link)
    
    def check_user_has_access(self, user_id: int, short_link: str) -> bool:
        """
        Verifica se o usuário tem acesso aos cliques associados a um determinado short_link.
        Retorna True se o usuário tem acesso, False caso contrário.
        """
        # Obter o usuário associado ao short_link
        link = self.db_session.query(LinkShortModel).filter(LinkShortModel.short_link == short_link).first()
        if link:
            if link.user_id == user_id:
                return True
        return False