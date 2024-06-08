import smtplib
import ssl
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Core.setting import settings

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
