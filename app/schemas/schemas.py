from pydantic import BaseModel,validator, datetime_parse
import re
from enum import Enum
from datetime import datetime,date

class StatusEnum(str, Enum):
    send = 'send'
    done = 'done'

class UserOut(BaseModel):
    email:str
    name:str

    class config():
        from_attributes = True
    
    
class Auth(UserOut):
    password: str

    class config():
        from_attributes = True

class UserIn(BaseModel):
    email:str
    name:str
    created_at:  date | None = None 
    password: str
    class config():
        from_attributes = True

class Login(BaseModel):
    username: str
    password: str

    class config():
        from_attributes = True

class LinkShortIn(BaseModel):
    link_long: str
    short_link: str

    class config():
        from_attributes = True

class MeLinkShort(BaseModel):
    link_long: str
    short_link: str
    qtd_clicks:int

    class config():
        from_attributes = True

class LinkShortOut(BaseModel):
    link_long: str

    class config():
        from_attributes = True


class ResetPasswordIn(BaseModel):
    user_id: int
    status: StatusEnum
    code: str

    class config():
        from_attributes = True

class ResetPasswordOut(BaseModel):
    user_id: str
    new_password: str

    class config():
        from_attributes = True

class ResetPassword(BaseModel):
    user_email: str 
    new_password:str

    class config():
        from_attributes = True


class ClickIn(BaseModel):
    link_short_id: str 
    user_agent: str | None
    ip: str
    localization: str | None

    class Config:
        from_attributes = True

class ClickOut(BaseModel):
    link_short_id: str 
    user_agent: str | None
    ip: str
    localization: str
    created_at: datetime | None 

    @validator('created_at', pre=True, always=True)
    def parse_date(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return value

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%d/%m/%Y %H:%M:%S") if v else None
        }
        
