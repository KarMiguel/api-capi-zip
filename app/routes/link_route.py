from fastapi import APIRouter,Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.auth_util import obter_usuario_logado 
from app.entity.depends import get_db_session
from app.repository.link_repository import RepositoryLink
from app.schemas.schemas import LinkShortOut
from app.schemas.schemas import LinkShortIn,LinkShortOut,MeLinkShort
import re
from app.entity.models import UserModel
from fastapi.responses import RedirectResponse

router = APIRouter(prefix='/api/v1/link')


@router.post('/shorten-link',status_code=status.HTTP_201_CREATED)
def short_link_auth(link: LinkShortOut, user_login: UserModel = Depends(obter_usuario_logado), db_session: Session = Depends(get_db_session)):
   
    pattern = re.compile(r'^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$')

    if not pattern.match(link.link_long):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="O link fornecido não está em formato web.")

    link_short_exist = RepositoryLink(db_session=db_session).obter_short_link(link.link_long,user_login.id)

    link_novo = LinkShortIn(link_long=link.link_long, short_link="")  
   
    if link_short_exist:
        link_novo.short_link = link_short_exist
        return {"link_long": link_novo.link_long,"link_short": link_short_exist}

    if not link_short_exist:
        link_novo.short_link = RepositoryLink(db_session=db_session).generate_link_short()
        link_salve = RepositoryLink(db_session=db_session).salve_link(link_novo, user_login.id)
        return {"link_log": link_salve.link_long, "link_short": link_salve.short_link}    


@router.post('/shorten-link-auth',status_code=status.HTTP_201_CREATED)
def short_link(link: LinkShortOut,db_session: Session = Depends(get_db_session)):
   
    pattern = re.compile(r'^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$')

    if not pattern.match(link.link_long):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="O link fornecido não está em formato web")

    link_short_exist = RepositoryLink(db_session=db_session).obter_short_link_sem_auth(link.link_long)

    link_novo = LinkShortIn(link_long=link.link_long, short_link="")  
   
    if link_short_exist:
        link_novo.short_link = link_short_exist
        return {"link_long": link_novo.link_long,"link_short": link_short_exist}

    if not link_short_exist:
        link_novo.short_link = RepositoryLink(db_session=db_session).generate_link_short()
        link_salve = RepositoryLink(db_session=db_session).salve_link(link_novo, 1)
        return {"link_log": link_salve.link_long, "link_short": link_salve.short_link}    



@router.get('/my-link-short', response_model=list[MeLinkShort],status_code=status.HTTP_200_OK)
def list_link(user: UserModel = Depends(obter_usuario_logado), db_session: Session = Depends(get_db_session)):
    repository_link = RepositoryLink(db_session=db_session)
    links = repository_link.list_all_short_link(user.id)

    me_links = []
    for link in links:
        qtd_clicks = repository_link.count_clicks_By_short_link(link.short_link)
        me_link = MeLinkShort(link_long=link.link_long, short_link=link.short_link, qtd_clicks=qtd_clicks)
        me_links.append(me_link)
    
    return me_links


@router.delete('/delete-short-link', status_code=status.HTTP_204_NO_CONTENT)
def delete_short_link(short_link: str, UserModel = Depends(obter_usuario_logado), db_session: Session = Depends(get_db_session)):
    deleted = RepositoryLink(db_session=db_session).delete_short_link(short_link)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link encurtado não encontrado.")

    return {"msg": f"{short_link} deletado com sucesso!"}


@router.get('/total-short-link')
def total_clicks(db_session: Session = Depends(get_db_session)):
    total = RepositoryLink(db_session=db_session).count_short_links();    
    return {"total":total}