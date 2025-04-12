from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime

class UserResponse(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)

class EmailRequest(BaseModel):
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    confirm_code: str = Field(..., min_length=6, max_length=6)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TwoFARequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class PasswordResetRequest(BaseModel):
    new_password: str = Field(..., min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class MessageResponse(BaseModel):
    message: str
    email: Optional[EmailStr] = None

class ESGRating(BaseModel):
    e: int = Field(..., ge=0, le=5)
    s: int = Field(..., ge=0, le=5)
    g: int = Field(..., ge=0, le=5)

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    full_description: Optional[str] = Field(None, min_length=10)
    category: Literal['ecology', 'social', 'governance']
    image: Optional[str] = None
    target_amount: float = Field(..., gt=0)
    end_date: datetime

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    full_description: Optional[str] = Field(None, min_length=10)
    category: Optional[Literal['ecology', 'social', 'governance']] = None
    image: Optional[str] = None
    current_amount: Optional[float] = Field(None, ge=0)
    target_amount: Optional[float] = Field(None, gt=0)
    days_left: Optional[int] = Field(None, ge=0)
    backers: Optional[int] = Field(None, ge=0)
    esg_rating: Optional[ESGRating] = None
    end_date: Optional[datetime] = None
    updates: Optional[List[str]] = None
    comments: Optional[List[str]] = None

class Project(ProjectBase):
    id: str
    current_amount: float = 0
    days_left: int
    backers: int = 0
    esg_rating: ESGRating
    created_at: datetime
    creator: str
    updates: Optional[List[str]] = None
    comments: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectListResponse(BaseModel):
    projects: List[Project]
