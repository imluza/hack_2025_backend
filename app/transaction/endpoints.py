from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.models import Project as ProjectModel, User, Transaction
from app.security import get_current_user
import uuid
from app.schemas import TransactionCreate, TransactionResponse
from ..database import get_db
from app.security import get_current_user
router = APIRouter(prefix="/transactions", tags=["transaction"])

@router.post("/new_transaction/")
async def create_transaction(
    transaction_data: TransactionCreate, db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    project = db.query(ProjectModel).filter(ProjectModel.id == transaction_data.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


    project.current_amount = Decimal(str(project.current_amount)) if isinstance(project.current_amount, float) else project.current_amount

    transaction_amount = Decimal(str(transaction_data.amount))

    project.current_amount += transaction_amount

    transaction_amount = Decimal(str(transaction_data.amount))
    transaction = Transaction(
        id=UUID(int=uuid.uuid4().int),
        user_id=user.id,
        project_id=transaction_data.project_id,
        project_title=project.title,
        amount=transaction_amount,
        status="completed",
    )

    db.add(transaction)
    db.commit()
    db.commit()

    return {"message": "Transaction successfully created and project updated"}
