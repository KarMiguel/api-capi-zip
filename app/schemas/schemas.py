from pydantic import BaseModal,validator

class User(BaseModal):
    username:str
    name:str

   
class Auth(User):
    password: str