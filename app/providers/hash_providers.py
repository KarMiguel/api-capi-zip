from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def gerar_hash(texto):
    return pwd_context.hash(texto)


def verificar_hash(texto, hash):
    return pwd_context.verify(texto, hash)