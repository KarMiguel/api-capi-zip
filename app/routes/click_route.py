from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from app.db.depends import get_db_session
from app.db.models import UserModel
from app.routes.auth_util import obter_usuario_logado 
from app.repository.link_repository import RepositoryLink
from fastapi.responses import RedirectResponse
from app.repository.click_repository import RepositoryClick, LinkShortModel
from app.schemas.schemas import ClickIn,ClickOut
from fastapi import HTTPException
from starlette.requests import Request
from sqlalchemy.orm.query import Query
import os
from dotenv import load_dotenv
from app.utils.UtilClicks import *


load_dotenv()

router = APIRouter()


@router.get('/l/{short_link}',response_class=RedirectResponse)
def redirect_to_original_link(short_link: str, request: Request, db_session: Session = Depends(get_db_session)):
    
    link_long = RepositoryLink(db_session=db_session).obter_short_link_generate(short_link)
    
    if not link_long:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link_short not found.")

    
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

@router.get('/me_click_short', response_model=list[ClickOut])
def list_click_short(short_link: str,user: UserModel = Depends(obter_usuario_logado),db_session: Session = Depends(get_db_session)):
    if not RepositoryClick(db_session).check_user_has_access(user.id, short_link):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not have access to clicks for this short link")

    clicks: Query = RepositoryClick(db_session).list_all_click_link(short_link)
    return clicks.all()


@router.get('/total_clicks')
def total_clicks(db_session: Session = Depends(get_db_session)):
    total = RepositoryLink(db_session=db_session).count_clicks();    
    return {"total":total}


