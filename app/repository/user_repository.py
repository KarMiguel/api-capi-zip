from email.policy import SMTP
from fastapi.exceptions import HTTPException
from sqlalchemy.orm  import Session
from app.db.models import UserModel,AuthModel,ResetPasswordModel
from app.schemas.schemas import ResetPasswordIn, UserIn, Auth
from fastapi import status
from sqlalchemy import select
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from dotenv import load_dotenv

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
        where(ResetPasswordModel.code==code).where(UserModel.email == email))
        return self.db_session.execute(query).scalar()


    def send_email(self, to_email, subject, body):
       
        SMTP_SERVER = os.getenv('SMTP_SERVER')
        SMTP_USER =os.getenv('SMTP_USER')
        SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
        
        if not SMTP_PASSWORD or  not SMTP_USER or not SMTP_SERVER:
            raise ValueError('Invalid email environment variables')
        smtp_server = SMTP_SERVER 
        smtp_port = 587
        smtp_user = SMTP_USER
        smtp_password = SMTP_PASSWORD
        from_email = SMTP_USER

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()

            server.login(smtp_user, smtp_password)

            server.sendmail(from_email, to_email, msg.as_string())

            server.quit()
                
        except smtplib.SMTPException as smtp_error:
            print(f'Error while sending email: {smtp_error}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Error sending email: {str(smtp_error)}'
            )
        except Exception as e:
            print(f'Unexpected error: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Unexpected error: {str(e)}'
            )
