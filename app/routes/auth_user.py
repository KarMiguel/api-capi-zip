import secrets
from fastapi import APIRouter,Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.routes.auth_util import obter_usuario_logado 
from app.db.depends import get_db_session
from app.repository.user_repository import UserUseCases
from app.schemas.schemas import UserIn,UserOut, Auth, Login,ResetPassword,LinkShortOut
from app.providers import hash_providers,token_providers
from datetime import datetime


router = APIRouter(prefix='/user')

@router.post('/register')
def register_user(user:Auth, db_session :Session = Depends(get_db_session)):

    
    located = UserUseCases(db_session = db_session).obter_por_usuario(user.email)
    
    if located :
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User already exists with this email')
    
    user.password = hash_providers.gerar_hash(user.password)
    uc  = UserUseCases(db_session = db_session).register(user)
   
    return {"id": uc.id, "user": uc.email}




@router.post('/login')
def login(login: Login, db_session=Depends(get_db_session)):
    senha = login.password
    username = login.username

    usuario = UserUseCases(db_session=db_session).obter_por_usuario(username)

    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There is no user with that username!')

    if usuario and hash_providers.verificar_hash(senha, usuario.auth.password):
        token = token_providers.criar_access_token({'sub': usuario.email})
        return {'user': usuario.id,"username":usuario.email,"acess":token}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Username or password incorrect!')
    
    
@router.get('/me', response_model=Login)
def me(usuario: Auth = Depends(obter_usuario_logado)):
    return usuario