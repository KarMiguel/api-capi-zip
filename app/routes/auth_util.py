from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status
from app.db.depends import  get_db_session
from app.providers import token_providers
from jose import JWTError
from app.repository.user_repository import UserUseCases


oauth2_schema = OAuth2PasswordBearer(tokenUrl= 'token')

def obter_usuario_logado(token:str = Depends(oauth2_schema),session: Session = Depends(get_db_session)):
    
    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Token Invalido')
  
    try:
        username = token_providers.verificar_access_token(token)
    except JWTError:
        raise exception
    
    if not  username:
        raise exception
    
    usuario = UserUseCases(session).obter_por_usuario(username)

    if not usuario:
        raise exception

    return usuario