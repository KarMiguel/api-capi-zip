from fastapi import APIRouter,Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routes.auth_util import obter_usuario_logado 
from app.db.depends import get_db_session
from app.repository.link_repository import RepositoryLink
from app.schemas.schemas import LinkShortOut
from app.schemas.schemas import LinkShortIn,LinkShortOut,MeLinkShort
import re
from app.db.models import UserModel
from fastapi.responses import RedirectResponse

router = APIRouter(prefix='/link')


@router.post('/short_link',status_code=status.HTTP_201_CREATED)
def short_link_auth(link: LinkShortOut, user_login: UserModel = Depends(obter_usuario_logado), db_session: Session = Depends(get_db_session)):
   
    pattern = re.compile(r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/?.*$')

    if not pattern.match(link.link_long):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="The link provided is not in web format")

    link_short_exist = RepositoryLink(db_session=db_session).obter_short_link(link.link_long,user_login.id)

    link_novo = LinkShortIn(link_long=link.link_long, short_link="")  
   
    if link_short_exist:
        link_novo.short_link = link_short_exist
        return {"link_long": link_novo.link_long,"link_short": link_short_exist}

    if not link_short_exist:
        link_novo.short_link = RepositoryLink(db_session=db_session).generate_link_short()
        link_salve = RepositoryLink(db_session=db_session).salve_link(link_novo, user_login.id)
        return {"link_log": link_salve.link_long, "link_short": link_salve.short_link}    


@router.get('/me_link_short/', response_model=list[MeLinkShort],status_code=status.HTTP_200_OK)
def list_link(user: UserModel = Depends(obter_usuario_logado), db_session: Session = Depends(get_db_session)):
    repository_link = RepositoryLink(db_session=db_session)
    links = repository_link.list_all_short_link(user.id)

    me_links = []
    for link in links:
        qtd_clicks = repository_link.count_clicks(link.short_link)
        me_link = MeLinkShort(link_long=link.link_long, short_link=link.short_link, qtd_clicks=qtd_clicks)
        me_links.append(me_link)
    
    return me_links

