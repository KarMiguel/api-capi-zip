import secrets
from fastapi import APIRouter,Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.entity.models import ResetPasswordModel, StatusReset
from app.utils.email_util import * 
from app.entity.depends import get_db_session
from app.repository.user_repository import UserUseCases
from app.schemas.schemas import ResetPassword, ResetPasswordIn,  StatusEnum, Auth, Login
from app.providers import hash_providers,token_providers
from datetime import datetime, timedelta


router = APIRouter(prefix='/api/v1/user')

@router.post('/register',status_code=status.HTTP_201_CREATED)
def register_user(user:Auth, db_session :Session = Depends(get_db_session)):
    
    located = UserUseCases(db_session = db_session).obter_por_usuario(user.email)
    
    if located :
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Já existe um usuário com este e-mail'
        )
    
    user.password = hash_providers.gerar_hash(user.password)
    UserUseCases(db_session = db_session).register(user)
   
    return {'message': 'Usuário criado com Sucesso!'}




@router.post('/login',status_code=status.HTTP_200_OK)
def login(login: Login, db_session=Depends(get_db_session)):
    senha = login.password
    username = login.username

    usuario = UserUseCases(db_session=db_session).obter_por_usuario(username)

    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Não há nenhum usuário com esse email!')

    if usuario and hash_providers.verificar_hash(senha, usuario.auth.password):
        token = token_providers.criar_access_token({'sub': usuario.email})
        return {"access_token":token}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Username ou senha incorreta!')

@router.patch('/reset-password',status_code = status.HTTP_200_OK)
def reset_password( user: ResetPassword, db_session: Session = Depends(get_db_session)):
    
    user_repository = UserUseCases(db_session=db_session)
    uc = user_repository.obter_por_usuario(user.user_email)
    if not uc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Usuário não cadastrado!')

    latest_reset_code = user_repository.get_latest_reset_password(user.user_email)
    if latest_reset_code and latest_reset_code.status == StatusEnum.send:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Um código de redefinição já foi enviado ao seu email.'
            )


    user_reset = ResetPasswordModel(
        code=secrets.token_urlsafe(24),
        status = StatusEnum.send,
        new_password = hash_providers.gerar_hash(user.new_password),
        created_at=datetime.utcnow() + timedelta(hours=1) 

    )
    uc.reset_passwords.append(user_reset)
    
    try:
        to_email = user.user_email
        send_email(to_email, user_reset.code)
    except Exception as e:
       raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro ao enviar e-mail de redefinição de senha:{str(e)}'
        )
    db_session.commit()
    return {'msg':'Código de confirmação enviado por e-mail.'}

        
@router.get('/reset-password/validate')
def valid_reset( email:str,code:str,db_session: Session = Depends(get_db_session)):
    
    user_repository = UserUseCases(db_session=db_session)
    user_reset = user_repository.get_reset_password(email, code)
        
    if not user_reset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Usuário não encontrado ou código de redefinição inválido'
        )
    
    latest_reset_code = user_repository.get_latest_reset_password(email)
    if user_reset != latest_reset_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='O código de redefinição fornecido já expirado.'
        )
    
    if user_reset.status == StatusEnum.done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='A senha já foi redefinida com este código.'
        )
    

    user_reset.user.auth.password = user_reset.new_password
    user_reset.status = StatusReset.done
    db_session.commit()

    return {'msg':'Senha redefinida com sucesso!'}
