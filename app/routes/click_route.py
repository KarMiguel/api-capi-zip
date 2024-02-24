import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from app.db.depends import get_db_session
from app.repository.link_repository import RepositoryLink
from fastapi.responses import RedirectResponse
from app.repository.click_repository import RepositoryClick
from app.schemas.schemas import ClickIn
router = APIRouter()

@router.get('/l/{short_link}', response_class=RedirectResponse)
def redirect_to_original_link(short_link: str, request: Request, db_session: Session = Depends(get_db_session)):
    link_long = RepositoryLink(db_session=db_session).obter_short_link_generate(short_link)
    
    if not link_long:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link_short not default.")
    
    #ip= request.headers.get('X-Forwarded-For')
    #ip = request.client.host
    ip = RepositoryClick(db_session).get_local_ip()
    user_agent = request.headers.get('user-agent') 
    
    print("IP: ", ip)
    print("user_agent: ",user_agent)
        
    #click= ClickIn(

    #   ip= RepositoryClick(db_session).get_local_ip(),
    #    user_agent =user_agent,
    #    localization= 'São Francisco',
    #)
    #RepositoryClick(db_session=db_session).salve_click(click,f"http://127.0.0.1:8000/l/{short_link}")*/

    return RedirectResponse(url=link_long.link_long)
