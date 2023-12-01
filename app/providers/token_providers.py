from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv('SECRET_kEY')
ALGORITHM = os.getenv('ALGORITHM')
EXPIRES_IN_MIN = 3000


def criar_access_token(data: dict):
    dados = data.copy()
    expiracao = datetime.utcnow() + timedelta(minutes=EXPIRES_IN_MIN)

    dados.update({'exp': expiracao})
    if not SECRET_KEY or not ALGORITHM:
        raise ValueError ("Variavel SECRET_KEY ou ALGORITHM nao encontrada")
    token_jwt = jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt


def verificar_access_token(token: str):
    if not SECRET_KEY or not ALGORITHM:
        raise ValueError ("Variavel SECRET_KEY ou ALGORITHM nao encontrada")
    carga = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return carga.get('sub')