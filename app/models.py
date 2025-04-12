from sqlalchemy import (
    Column, String, Integer, Numeric, UUID, Boolean,
    DateTime, ForeignKey, CheckConstraint, Text
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM
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
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    code_2fa = Column(Integer)
    status = Column(String(20))

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    full_description = Column(Text)
    category = Column(String, nullable=False)
    image = Column(String)
    current_amount = Column(Numeric, default=0)
    target_amount = Column(Numeric, nullable=False)
    days_left = Column(Integer, nullable=False)
    backers = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    creator_name = Column(String)
    creator_avatar = Column(String)
    esg_e = Column(Integer)
    esg_s = Column(Integer)
    esg_g = Column(Integer)
    esg_total = Column(Integer)

    __table_args__ = (
        CheckConstraint("category IN ('ecology', 'social', 'governance')", name="check_category"),
        CheckConstraint("esg_e BETWEEN 0 AND 5", name="check_esg_e"),
        CheckConstraint("esg_s BETWEEN 0 AND 5", name="check_esg_s"),
        CheckConstraint("esg_g BETWEEN 0 AND 5", name="check_esg_g"),
        CheckConstraint("esg_total BETWEEN 0 AND 15", name="check_esg_total"),
    )

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String)
    earned_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

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
