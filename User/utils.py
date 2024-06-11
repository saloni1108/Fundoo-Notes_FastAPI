import smtplib
import ssl
import jwt
from passlib.context import CryptContext
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from setting import settings
from datetime import datetime, timedelta
from jwt import PyJWTError
from fastapi import HTTPException
from enum import Enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def send_email(to_mail: str, mail_subject: str, mail_body: str):
    msg = EmailMessage()
    msg["Subject"] = "Welcome to the Application"
    msg["From"] = settings.SMTP_USERNAME
    msg["To"] = to_mail
    msg.attach(MIMEText(mail_body, 'plain'))
    msg.set_content(mail_body)

    with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT, context = ssl.create_default_context()) as smtp:
        smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        # smtp.send_message(msg)
        smtp.sendmail(settings.SMTP_USERNAME, to_mail, msg.as_string())
        smtp.quit()


class Audience(Enum):
    register = "register_user"
    login = "login_user"

def encoded_user_jwt(payload: dict):
    if "exp" not in payload:
        payload["exp"] = datetime.utcnow() + timedelta(hours = 1)
    encoded_token = jwt.encode(payload = payload, key = settings.SECRET_KEY, algorithm = settings.ALGORITHM)
    return encoded_token

def decoded_user_jwt(token: str, audience: str)->dict:
    try:
        decoded_token = jwt.decode(token, key = settings.SECRET_KEY, algorithms = [settings.ALGORITHM], audience = audience)
    except PyJWTError:
        raise HTTPException(detail = "Invalid JWT Token", status_code = 401)
    return decoded_token