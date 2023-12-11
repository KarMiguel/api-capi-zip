from fastapi import APIRouter,Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routes.auth_util import obter_usuario_logado 
from app.db.depends import get_db_session
from app.repository.link_repository import RepositoryLink
from app.schemas.schemas import LinkShortOut
from app.schemas.schemas import LinkShortIn,LinkShortOut
import re
from app.db.models import UserModel
from fastapi.responses import RedirectResponse

router = APIRouter(prefix='/link')


@router.post('/short_link')
def short_link(link: LinkShortOut, user_login: UserModel = Depends(obter_usuario_logado), db_session: Session = Depends(get_db_session)):
   
    pattern = re.compile(r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/?.*$')

    if not pattern.match(link.link_long):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="The link provided is not in web format")

    link_short_exist = RepositoryLink(db_session=db_session).obter_short_link_generate(link.link_long)

    link_novo = LinkShortIn(link_long=link.link_long, short_link="")  
   
    if link_short_exist:
        link_novo.short_link = link_short_exist
        return {"link_long": link_novo.link_long,"link_short": link_short_exist}

    if not link_short_exist:
        link_novo.short_link = RepositoryLink(db_session=db_session).generate_link_short()
        link_salve = RepositoryLink(db_session=db_session).salve_link(link_novo, user_login.id)
        return {"link_log": link_salve.link_long, "link_short": link_salve.short_link}
    
@router.get('/{short_link}', response_class=RedirectResponse)
def redirect_to_original_link(short_link: str, db_session: Session = Depends(get_db_session)):
    link_long = RepositoryLink(db_session=db_session).obter_short_link_generate(short_link)
    
    if not link_long:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link_short not default.")
    
    return RedirectResponse(url=link_long)

@router.get('/me_link_short/',response_model=list[LinkShortIn])
def list_link(user: UserModel =  Depends(obter_usuario_logado) , db_session: Session = Depends(get_db_session)):
    link = RepositoryLink(db_session=db_session).list_all_short_link(user.id)
    return link
