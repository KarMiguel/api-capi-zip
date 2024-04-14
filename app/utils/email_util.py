import base64
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from fastapi.exceptions import HTTPException
from fastapi import status
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, code):
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    
    if not SMTP_PASSWORD or not SMTP_USER or not SMTP_SERVER:
        raise ValueError('Invalid email environment variables')
    
    smtp_server = SMTP_SERVER 
    smtp_port = 587
    smtp_user = SMTP_USER
    smtp_password = SMTP_PASSWORD
    from_email = SMTP_USER
    
    msg = MIMEMultipart('related')
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Redefinição de Senha"
 
    html_body = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redefinição de Senha</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        
        <div style="background-color: #ffffff; padding: 30px; border-radius: 10px; text-align: center;">
            <h2>Redefinição de Senha da Cap Zip</h2>
        
                <div style="text-align: center; margin-bottom: 20px;">
                <p>Você solicitou a redefinição de senha para a sua conta.</p>
                <img src="cid:image1" style="max-width: 50%; height: auto;">
        </div>
            <p>Copie código abaixo e cole no campo código para redefinir sua senha.  </p>
            <p>Código: <b>{}</b></p>
        </div>
    </div>
    </body>
    </html>
    """.format(code)

    msg.attach(MIMEText(html_body.format(code), 'html'))
    
    # Anexar a imagem
    image_path = "app/utils/LogoOficialCut.png"
    with open(image_path, 'rb') as img_file:
        image = MIMEImage(img_file.read())
        image.add_header('Content-ID', '<image1>')
        msg.attach(image)

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
