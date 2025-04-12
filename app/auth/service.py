import random
import hashlib
import time
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from .email_service import send_verification_email, send_password_email
from app.models import VerificationCode, User
from app.database import get_db
from app.security import create_access_token

def generate_code() -> str:
    return ''.join([str(random.randint(1, 9)) for _ in range(6)])

def hash_password(password: str) -> str:
    return hashlib.sha512(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def generate_random_password() -> str:
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(12))

async def send_verification_code(email: str, db):
    existing_code = db.query(VerificationCode).filter(
        VerificationCode.email == email,
        VerificationCode.expires_at > datetime.utcnow()
    ).first()

    if existing_code:
        time_left = (existing_code.expires_at - datetime.utcnow()).seconds
        if time_left > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Код уже отправлен. Повторный запрос возможен через 60 секунд"
            )

    code = generate_code()
    expires_at = datetime.utcnow() + timedelta(minutes=1)

    verification_code = VerificationCode(
        email=email,
        code=code,
        expires_at=expires_at
    )
    db.add(verification_code)
    db.commit()

    await send_verification_email(email, code)

    return code

async def send_recovered_password(email: str, subject:str, body:str):
    await send_password_email(email, subject, body)
