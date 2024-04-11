from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from app.entity.depends import get_db_session
from app.entity.models import UserModel
from app.utils.auth_util import obter_usuario_logado 
from app.repository.link_repository import RepositoryLink
from fastapi.responses import RedirectResponse
from app.repository.click_repository import RepositoryClick, LinkShortModel
from app.schemas.schemas import ClickIn,ClickOut
from fastapi import HTTPException
from starlette.requests import Request
from sqlalchemy.orm.query import Query
import os
from dotenv import load_dotenv
from app.utils.clicks_util import *


load_dotenv()

router = APIRouter()


@router.get('/l/{short_link}',response_class=RedirectResponse)
def redirect_to_original_link(short_link: str, request: Request, db_session: Session = Depends(get_db_session)):
    
    link_long = RepositoryLink(db_session=db_session).obter_short_link_generate(short_link)
    
    if not link_long:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link encurtado não encontrado.")

    
    if  RepositoryLink(db_session=db_session).short_link_By_Id(1,link_long) :
        ip = get_from_ip()
        user_agent = request.headers.get('user-agent') 
        localization = get_location_from_ip(ip) 
        
        DOMAIN_URL = os.getenv("DOMAIN_URL")
        if not DOMAIN_URL:
            raise ValueError("Domain not defined")
        
        print(f"Shor Link: {DOMAIN_URL}/l/{short_link}")    
        print("IP: ",ip)
        print("User_agent: ",user_agent)
        print("Localization: ",localization)

        click = ClickIn(
            link_short_id= f'{DOMAIN_URL}/l/{short_link}',
            user_agent=user_agent,
            ip=ip,
            localization=localization
        )
        RepositoryClick(db_session=db_session).salve_click(click, short_link)

    return RedirectResponse(url=link_long.link_long)

@router.get('/api/v1/click/my-shortened', response_model=list[ClickOut])
def list_click_short(short_link: str,user: UserModel = Depends(obter_usuario_logado),db_session: Session = Depends(get_db_session)):
    if not RepositoryClick(db_session).check_user_has_access(user.id, short_link):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{user.email}, você não tem acesso aos cliques deste link encurtado."
            )

    clicks =  RepositoryClick(db_session).list_all_click_link(short_link)
    return clicks


@router.get('/api/v1/total-clicks')
def total_clicks(db_session: Session = Depends(get_db_session)):
    total = RepositoryClick(db_session=db_session).count_clicks()    
    return {"total":total}


