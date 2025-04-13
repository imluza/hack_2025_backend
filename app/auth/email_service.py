import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from fastapi import HTTPException, status
from dotenv import load_dotenv
from fastapi import HTTPException
from app.models import User

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


async def send_password_email(to: str, subject: str, body: str):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("PASSWORD_EMAIL")
    display_name = os.getenv("DISPLAY_NAME")

    message = MIMEMultipart()
    message["From"] = f'"{display_name}" <{sender_email}>'
    message["To"] = to
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, to, message.as_string())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отправке письма: {e}"
        )
    finally:
        server.quit()


async def send_email_to_admins(project_id, project_title, analyze_result, body_of_response, db):

    admins = db.query(User).filter(User.role == "admin").all()
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("PASSWORD_EMAIL")
    display_name = os.getenv("DISPLAY_NAME")
    for admin in admins:
        message = MIMEMultipart()
        message["From"] = f'"{display_name}" <{sender_email}>'
        message["To"] = admin.email
        message["Subject"] = "Утверждение проекта"

        body = f"Недавно размещенный проект не проходит контроль. Перейдите в панель управления для просмотра информации\nАйди:     {project_id}\n Название:    {project_title}"
        body += f"\n\nОтвет Модели:\n{body_of_response}"
        message.attach(MIMEText(body, "plain"))
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, admin.email, message.as_string())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при отправке письма: {e}"
            )
        finally:
            server.quit()
