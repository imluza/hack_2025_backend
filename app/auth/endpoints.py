from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import (
    UserRegister, EmailRequest, VerifyEmailRequest,
    LoginRequest, TwoFARequest, PasswordResetRequest,
    MessageResponse, TokenResponse
)
from .service import (
    hash_password, verify_password, generate_code,
    send_verification_code, generate_random_password
)
from app.security import create_access_token
from app.models import User, VerificationCode
from ..database import get_db
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=MessageResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    await send_verification_code(user_data.email, db)

    return MessageResponse(
        email=user_data.email,
        message="Код подтверждения отправлен на указанную почту"
    )

@router.post("/register-send-email-verification", response_model=MessageResponse)
async def send_email_verification(email_data: EmailRequest, db: Session = Depends(get_db)):
    await send_verification_code(email_data.email, db)
    return MessageResponse(
        email=email_data.email,
        message="Код подтверждения отправлен на указанную почту"
    )

@router.post("/register-verify-email", response_model=MessageResponse)
async def verify_email(verify_data: VerifyEmailRequest, db: Session = Depends(get_db)):
    verification = db.query(VerificationCode).filter(
        VerificationCode.email == verify_data.email,
        VerificationCode.code == verify_data.confirm_code,
        VerificationCode.expires_at > datetime.utcnow()
    ).first()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код неверный или истёк срок действия"
        )

    return MessageResponse(
        email=verify_data.email,
        message="Почта подтверждена успешно"
    )

@router.post("/login", response_model=MessageResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    await send_verification_code(login_data.email, db)

    return MessageResponse(
        message="Логин верный. Отправлен код подтверждения на email"
    )

@router.post("/2fa", response_model=TokenResponse)
async def verify_2fa(twofa_data: TwoFARequest, db: Session = Depends(get_db)):
    verification = db.query(VerificationCode).filter(
        VerificationCode.email == twofa_data.email,
        VerificationCode.code == twofa_data.code,
        VerificationCode.expires_at > datetime.utcnow()
    ).first()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код или срок действия истёк"
        )

    user = db.query(User).filter(User.email == twofa_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    access_token = create_access_token(data={"sub": user.email})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )

@router.post("/password/recovery", response_model=MessageResponse)
async def password_recovery(email_data: EmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким email не найден"
        )

    new_password = generate_random_password()
    user.password_hash = hash_password(new_password)
    db.commit()

    return MessageResponse(
        message="Новый пароль был отправлен на вашу почту"
    )

@router.post("/password/reset", response_model=MessageResponse)
async def password_reset(reset_data: PasswordResetRequest, db: Session = Depends(get_db)):
    return MessageResponse(
        message="Пароль успешно изменён"
    )
