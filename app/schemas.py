from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List, Literal
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

class UserResponse(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    role: str
    id: UUID
    photo: str

class CommentCreate(BaseModel):
    project_id: UUID
    content: str

class CommentResponse(BaseModel):
    id: UUID
    project_id: UUID
    content: str
    date: datetime
    author_id: UUID
    author_name: str | None
    author_avatar: str | None

    class Config:
        orm_mode = True

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)

class EmailRequest(BaseModel):
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    confirm_code: str = Field(..., min_length=6, max_length=6)

class TransactionCreate(BaseModel):
    project_id: UUID
    amount: Decimal

    class Config:
        orm_mode = True

class TransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    project_id: UUID
    project_title: str
    amount: Decimal
    date: datetime
    status: str

    class Config:
        orm_mode = True

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

    @field_validator('end_date')
    def validate_end_date(cls, v):
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

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
    id: UUID
    creator_id: UUID
    current_amount: float = 0
    days_left: int
    backers: int = 0
    esg_rating: ESGRating
    created_at: datetime
    creator_name: str
    creator_avatar: Optional[str] = None

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            title=obj.title,
            description=obj.description,
            full_description=obj.full_description,
            category=obj.category,
            image=obj.image,
            current_amount=obj.current_amount,
            target_amount=obj.target_amount,
            days_left=obj.days_left,
            backers=obj.backers,
            esg_rating=ESGRating(e=obj.esg_e, s=obj.esg_s, g=obj.esg_g),
            created_at=obj.created_at,
            end_date=obj.end_date,
            creator_id=obj.creator_id,
            creator_name=obj.creator_name,
            creator_avatar=obj.creator_avatar
        )

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }
    )

class ProjectListResponse(BaseModel):
    projects: List[Project]
