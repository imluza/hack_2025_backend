from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import (
    UserRegister, EmailRequest, VerifyEmailRequest,
    LoginRequest, TwoFARequest, PasswordResetRequest,
    MessageResponse, TokenResponse
)
from .service import (
    hash_password, verify_password, generate_code,
    send_verification_code, generate_random_password,
    send_recovered_password
)
from app.security import create_access_token
from app.models import User, VerificationCode
from ..database import get_db
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=MessageResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    hashed_password = hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password,
        is_active=False
    )
    db.add(new_user)
    db.commit()

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

    user = db.query(User).filter(User.email == verify_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    user.is_active = True
    db.commit()

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
        email=login_data.email,
        message="Отправлен код подтверждения на email"
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

    email_subject = "Восстановление пароля"
    email_body = (
        f"Здравствуйте, {user.email}!\n\n"
        f"Ваш новый пароль: {new_password}\n\n"
        f"Пожалуйста, смените его после входа в систему.\n"
        f"Если вы не запрашивали восстановление, просто проигнорируйте это сообщение."
    )
    await send_recovered_password(email=user.email, subject=email_subject, body=email_body)

    return MessageResponse(
        message="Новый пароль был отправлен на вашу почту",
        email = user.email
    )
