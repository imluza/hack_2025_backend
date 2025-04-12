import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from fastapi import HTTPException, status
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

async def send_verification_email(email: str, code: str):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("PASSWORD_EMAIL")
    display_name = os.getenv("DISPLAY_NAME")

    message = MIMEMultipart()
    message["From"] = f'"{display_name}" <{sender_email}>'
    message["To"] = email
    message["Subject"] = "Код подтверждения"

    body = f"Ваш код подтверждения: {code}\nКод действителен в течение 5 минут."
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, email, message.as_string())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отправке письма: {e}"
        )
    finally:
        server.quit()
