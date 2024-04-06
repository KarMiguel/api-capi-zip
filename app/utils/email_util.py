from email.policy import SMTP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from fastapi.exceptions import HTTPException
from fastapi import status
from dotenv import load_dotenv
load_dotenv()


def send_email(to_email, subject, body):
    
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
