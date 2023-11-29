from fastapi.exceptions import HTTPException
from sqlalchemy.orm  import Session
from app.db.models import UserModel,AuthModel
from app.schemas.schemas import UserIn, Auth,ResetPassword
from fastapi import status
from sqlalchemy import select, insert
import smtplib
from sqlalchemy.orm import joinedload
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class UserUseCases:
    def __init__(self,db_session:Session) :
        self.db_session = db_session

    def register(self, user: Auth)->UserModel:
        user_model = UserModel(
            email=user.email,
            name=user.name,
            created_at=datetime.utcnow()
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
    

    def change_password(self, reset_password: ResetPassword, new_password: str):
        user_id = reset_password.user_id
        auth_model = self.db_session.query(AuthModel).filter_by(user_id=user_id).first()

        if not auth_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
    
    
        auth_model.password = new_password
        self.db_session.commit()


    def send_email(self, to_email, subject, body):
        smtp_server = "your_smtp_server"
        smtp_port = 587
        smtp_user = "your_smtp_user"
        smtp_password = "your_smtp_password"
        from_email = "your_from_email"

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())