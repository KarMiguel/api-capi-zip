from sqlalchemy.orm  import Session
from app.db.model.models import UserModel,AuthModel,ResetPasswordModel
from app.schemas.schemas import ResetPasswordIn, UserIn, Auth
from sqlalchemy import select
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import desc

load_dotenv()

class UserUseCases:
    def __init__(self,db_session:Session) :
        self.db_session = db_session

    def register(self, user: Auth)->UserModel:
        user_model = UserModel(
            email=user.email,
            name=user.name,
            created_at = datetime.utcnow()
        )
        
        auth_model = AuthModel(
            password=user.password
        )
        user_model.auth = auth_model
        self.db_session.add(user_model)
        self.db_session.commit()
        self.db_session.refresh(user_model)
       
        return user_model
    
    
    def obter_por_usuario(self, username):
        query = select(UserModel).where(
            UserModel.email == username
        
        )
        return self.db_session.execute(query).scalar()
    

    def reset_password(self,rp: ResetPasswordIn):
        reset_model = ResetPasswordModel(
            user_id = rp.user_id,
            status= rp.status,
            code = rp.code
        )
        self.db_session.add( reset_model)
        self.db_session.commit()
        return reset_model

    def get_reset_password(self,email,code)->ResetPasswordModel | None:
        query = (select(ResetPasswordModel).join(UserModel.reset_passwords).
        where(ResetPasswordModel.code == code).where(UserModel.email == email))
        return self.db_session.execute(query).scalar()

    def get_latest_reset_password(self, email):
        query = (
            select(ResetPasswordModel)
            .join(UserModel.reset_passwords)
            .filter(UserModel.email == email)
            .order_by(desc(ResetPasswordModel.created_at)) 
            .limit(1)  
        )
        return self.db_session.execute(query).scalar()