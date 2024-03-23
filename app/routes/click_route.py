import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from app.db.depends import get_db_session
from app.db.models import ClickModel,UserModel
from app.routes.auth_util import obter_usuario_logado 
from app.repository.link_repository import RepositoryLink
from fastapi.responses import RedirectResponse
from app.repository.click_repository import RepositoryClick
from app.schemas.schemas import ClickIn,ClickOut
from fastapi import HTTPException
from geopy.geocoders import Nominatim
from starlette.requests import Request
from sqlalchemy.orm.query import Query
router = APIRouter()

def get_city_from_ip(request: Request) -> str:
    ip = request.client.host
    try:
        geolocator = Nominatim(user_agent="fastapi_app")
        location = geolocator.geocode(ip)
        if location and hasattr(location, 'address'):
            city = location.address.split(",")[-3].strip()  
            return city
        else:
            return "Unknown"
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve city from IP.") from e

@router.get('/l/{short_link}',response_class=RedirectResponse)
def redirect_to_original_link(short_link: str, request: Request, db_session: Session = Depends(get_db_session)):
    link_long = RepositoryLink(db_session=db_session).obter_short_link_generate(short_link)
    
    if not link_long:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link_short not found.")
    
    ip = request.client.host
    user_agent = request.headers.get('user-agent') 
    localization = get_city_from_ip(request) or "São Francisco - MG"

    print("Shor Link: ",short_link)    
    print("IP: ",ip)
    print("User_agent: ",user_agent)
    print("Localization: ",localization)
    
    click = ClickIn(
        link_short_id= f'http://127.0.0.1:8000/l/{short_link}',
        user_agent=user_agent,
        ip=ip,
        localization=localization
    )
    RepositoryClick(db_session=db_session).salve_click(click, short_link)

    return RedirectResponse(url=link_long.link_long)

@router.get('/me_click_short', response_model=list[ClickOut])
def list_click_short(short_link: str,user: UserModel = Depends(obter_usuario_logado),db_session: Session = Depends(get_db_session)):
    if not RepositoryClick(db_session).check_user_has_access(user.id, short_link):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to clicks for this short link")

    clicks: Query = RepositoryClick(db_session).list_all_click_link(short_link)
    return clicks.all()