import secrets
from fastapi import APIRouter,Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import ResetPasswordModel, StatusReset
from app.routes.auth_util import obter_usuario_logado 
from app.db.depends import get_db_session
from app.repository.user_repository import UserUseCases
from app.schemas.schemas import ResetPassword, ResetPasswordIn,  StatusEnum, Auth, Login
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
        return {"acess_token":token}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Username or password incorrect!')

@router.post('/reset_password',status_code = 204)
def reset_password( user: ResetPassword, db_session: Session = Depends(get_db_session)):
    
    uc = UserUseCases(db_session=db_session).obter_por_usuario(user.user_email)
    if not uc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='user not register!')

    
    user_reset = ResetPasswordModel(
        code=secrets.token_urlsafe(24),
        status = StatusEnum.send,
        new_password = hash_providers.gerar_hash(user.new_password)
    )
    uc.reset_passwords.append(user_reset)
    
    try:
        to_email = user.user_email
        subject = f'Redefinição de senha'
        body = f'Confirme o código para prosseguir!\nCódigo = {user_reset.code}'
        UserUseCases(db_session=db_session).send_email(to_email, subject, body)
    except Exception as e:
       raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro ao enviar e-mail de redefinição de senha:{str(e)}'
        )
    db_session.commit()
    return {'msg':'Confirmation code sent in email'}
        
@router.get('/valid_reset')
def valid_reset( email:str,code:str,db_session: Session = Depends(get_db_session)):
    
    user_reset = UserUseCases(db_session=db_session).get_reset_password(email,code)
    
    if not user_reset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'user not foud'
        )
    user_reset.user.auth.password = user_reset.new_password
    user_reset.status = StatusReset.done
    db_session.commit()

    return {'msg':'Password reset successfully'}



@router.get('/me', response_model=Login)
def me(usuario: Auth = Depends(obter_usuario_logado)):
    return usuario