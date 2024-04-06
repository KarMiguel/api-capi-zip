from operator import and_
from sqlalchemy import func
from app.entity.models import LinkShortModel,ClickModel
from sqlalchemy.orm  import Session
from app.entity.depends import  get_db_session
from app.schemas.schemas import Auth, LinkShortIn,  UserIn
from sqlalchemy.sql.expression import select
import random
import string
import os
from dotenv import load_dotenv
load_dotenv()

class RepositoryLink:
    def __init__(self,db_session:Session) :
        self.db_session = db_session
    
    def salve_link(self,link: LinkShortIn,user_id:int ):
        link_model = LinkShortModel(
            user_id = user_id,
            link_long = link.link_long,
            short_link = link.short_link
        )
        self.db_session.add(link_model)    
        self.db_session.commit()
        self.db_session.refresh(link_model)

        return link_model
    

    def generate_link_short(self):
        self.caracteres = string.ascii_letters + string.digits
        self.links_gerados = set()

        while True:
            novo_link = ''.join(random.sample(self.caracteres, 5))
            DOMAIN_URL = os.getenv("DOMAIN_URL")
            if not DOMAIN_URL:
                raise ValueError("Domain not defined")
            new_full_link = f'{DOMAIN_URL}/l/{novo_link}'
            if new_full_link not in self.links_gerados and not self.obter_short_link_generate(new_full_link):
                self.links_gerados.add(new_full_link)
                return new_full_link
    
    
    def obter_short_link_generate(self, link):
        DOMAIN_URL = os.getenv("DOMAIN_URL")
        if not DOMAIN_URL:
            raise ValueError("Domain not defined2")
        link_short = f'{DOMAIN_URL}/l/{link}'
        print(link_short)
        query = select(LinkShortModel).where(
        LinkShortModel.short_link == link_short
    )
        short_link_result = self.db_session.execute(query).scalar()
        print(short_link_result)
        short_link = short_link_result if short_link_result else None
    
        return short_link
    
    def obter_short_link(self, link_long, user_id):
        existing_link = self.db_session.query(LinkShortModel).filter(
            LinkShortModel.link_long == link_long,
            LinkShortModel.user_id == user_id
        ).first()

        if existing_link:
            return existing_link.short_link
        else:
            return None
    
    def obter_short_link_sem_auth(self, link_long):
        existing_link = self.db_session.query(LinkShortModel).filter(
            LinkShortModel.link_long == link_long
        ).first()

        if existing_link:
            return existing_link.short_link
        else:
            return None
    
    def count_clicks_By_short_link(self, short_link):
        return self.db_session.query(func.count()).join(LinkShortModel.clicks).filter(LinkShortModel.short_link == short_link).scalar()

    def list_all_short_link(self, user_id: int):
        query = select(LinkShortModel).where(LinkShortModel.user_id == user_id)
        resultado = self.db_session.execute(query).scalars().all()
        return resultado
    
    def delete_short_link(self, short_link):
        link = self.db_session.query(LinkShortModel).filter(LinkShortModel.short_link == short_link).first()
        if link:
            self.db_session.query(ClickModel).filter(ClickModel.link_short_id == short_link).delete()
            self.db_session.delete(link)
            self.db_session.commit()
            return True
        return False
    
    def short_link_By_Id(self, user_id: int,link):
        query = select(LinkShortModel).where(
            and_(
                LinkShortModel.user_id != user_id,
                LinkShortModel.short_link == link.short_link
            )
        )
        resultado = self.db_session.execute(query).scalars().all()
        return resultado
   
    def count_short_links(self):
        return self.db_session.query(func.count(LinkShortModel.short_link)).scalar()

        