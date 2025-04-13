from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime, timedelta, timezone
from app.security import get_current_user
from ..database import get_db
from app.models import Project as ProjectModel, User
from app.schemas import (
    ProjectCreate, ProjectUpdate, Project,
    ProjectListResponse, ESGRating
)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=ProjectListResponse)
def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    db_projects = db.query(ProjectModel).offset(skip).limit(limit).all()
    projects = [Project.from_orm(project) for project in db_projects]
    return {"projects": projects}

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: Request, 
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    headers = request.headers
    print("Headers:", headers)

    body = await request.body()
    print("Body:", body.decode())

    end_date = project_data.end_date
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    days_left = (end_date - datetime.now(timezone.utc)).days

    project = ProjectModel(
        id=str(uuid.uuid4()),
        title=project_data.title,
        description=project_data.description,
        full_description=project_data.full_description,
        category=project_data.category,
        image=project_data.image,
        current_amount=0,
        target_amount=project_data.target_amount,
        days_left=days_left,
        backers=0,
        esg_e=0,
        esg_s=0,
        esg_g=0,
        created_at=datetime.now(timezone.utc),
        end_date=end_date,
        creator_id=str(current_user.id),
        creator_name=current_user.name,
        creator_avatar=current_user.avatar
    )

    db.add(project)
    db.commit()
    db.refresh(project)
    return Project.from_orm(project)

@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return Project.from_orm(project)

@router.patch("/{project_id}", response_model=Project)
def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if project.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own projects"
        )

    update_data = project_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "esg_rating":
            project.esg_e = value.get('e', project.esg_e)
            project.esg_s = value.get('s', project.esg_s)
            project.esg_g = value.get('g', project.esg_g)
        elif field == "end_date":
            setattr(project, field, value)
            project.days_left = (value - datetime.now(timezone.utc)).days
        elif field not in ["updates", "comments"]:
            setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return Project.from_orm(project)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if project.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own projects"
        )

    db.delete(project)
    db.commit()
    return None
