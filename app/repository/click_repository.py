from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from app.repository.link_repository import RepositoryLink
from app.schemas.schemas import*
from app.entity.models import ClickModel,LinkShortModel
from datetime import datetime,time
from sqlalchemy import func, case


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
        
    def list_all_click_link(self, short_link: str):
        return self.db_session.query(ClickModel).filter(ClickModel.link_short_id == short_link)
      

    def check_user_has_access(self, user_id: int, short_link: str) -> bool:
       
        link = self.db_session.query(LinkShortModel).filter(LinkShortModel.short_link == short_link).first()
        if link:
            if link.user_id == user_id:
                return True
        return False
    
     
    def count_clicks(self):
        return self.db_session.query(func.count(ClickModel.link_short_id)).scalar()
    
    def get_clicks_by_city(self,link: str):
        clicks_info = []
        # Obtém os cliques agrupados por localização (cidade) para o link fornecido
        clicks_by_city = (
            self.db_session.query(
                ClickModel.localization,
                func.count(ClickModel.id).label('clicks_count')
            )
            .join(ClickModel.link_short)
            .filter(LinkShortModel.short_link == link)
            .group_by(ClickModel.localization)
            .order_by(func.count(ClickModel.id).desc())
            .all()
        )

        # Converte os resultados em objetos ClickCity
        for city, click_count in clicks_by_city:
            clicks_info.append(ClickCity(city=city, qtd_clicks=click_count))

        return clicks_info
      
    def get_clicks_by_period(self, short_link: str):
        manha_start = time(6, 0)  # Manhã começa às 6:00
        tarde_start = time(12, 0)  # Tarde começa ao meio-dia
        noite_start = time(18, 0)  # Noite começa às 18:00

        manha_clicks = (
            self.db_session.query(func.count(ClickModel.id))
            .filter(
                ClickModel.link_short_id == short_link,
                func.extract('hour', ClickModel.created_at) < tarde_start.hour
            )
            .scalar()
        )

        tarde_clicks = (
            self.db_session.query(func.count(ClickModel.id))
            .filter(
                ClickModel.link_short_id == short_link,
                func.extract('hour', ClickModel.created_at) >= tarde_start.hour,
                func.extract('hour', ClickModel.created_at) < noite_start.hour
            )
            .scalar()
        )

        noite_clicks = (
            self.db_session.query(func.count(ClickModel.id))
            .filter(
                ClickModel.link_short_id == short_link,
                func.extract('hour', ClickModel.created_at) >= noite_start.hour
            )
            .scalar()
        )

        return manha_clicks, tarde_clicks, noite_clicks
