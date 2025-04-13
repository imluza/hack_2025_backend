from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean,
    DateTime, ForeignKey, CheckConstraint, Text,
    Float
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM, UUID
from .database import Base
import uuid
from datetime import datetime


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    code = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    avatar = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=False)
    role = Column(String(10), default="user")

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    full_description = Column(Text)
    category = Column(String(20), nullable=False)
    image = Column(String(255))
    current_amount = Column(Float, default=0)
    target_amount = Column(Float, nullable=False)
    days_left = Column(Integer)
    backers = Column(Integer, default=0)
    esg_e = Column(Integer, default=0)
    esg_s = Column(Integer, default=0)
    esg_g = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    creator_name = Column(String(100))
    creator_avatar = Column(String(255))
    is_active = Column(Boolean, default=False)
class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String)
    earned_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"))
    project_title = Column(String)
    amount = Column(Numeric, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    status = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('completed', 'pending', 'failed')", name="check_status"),
    )

class ProjectUpdate(Base):
    __tablename__ = "project_updates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    author_name = Column(String)
    author_avatar = Column(String)

class ProjectComment(Base):
    __tablename__ = "project_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    author_name = Column(String)
    author_avatar = Column(String)

class BackedProject(Base):
    __tablename__ = "backed_projects"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)

class EcoWallet(Base):
    __tablename__ = "eco_wallets"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    co2_saved = Column(Numeric, default=0)
    trees_planted = Column(Integer, default=0)
    water_saved = Column(Numeric, default=0)
