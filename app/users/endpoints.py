from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.schemas import (
    UserRegister, EmailRequest, VerifyEmailRequest,
    LoginRequest, TwoFARequest, PasswordResetRequest,
    MessageResponse, TokenResponse, UserResponse
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.security import create_access_token
from app.models import User, VerificationCode
from ..database import get_db
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 360))
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/get_me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user)
):
    return {
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "id": user.id,
        "photo": user.avatar
    }
