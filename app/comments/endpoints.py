from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.models import ProjectComment, User
from app.schemas import CommentCreate, CommentResponse
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/new_comment", response_model=CommentResponse)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_comment = ProjectComment(
        project_id=comment.project_id,
        content=comment.content,
        author_id=current_user.id,
        author_name=current_user.name,
        author_avatar=current_user.avatar
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment
