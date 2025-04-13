from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from fastapi import FastAPI, HTTPException, status
from jose import JWTError, jwt
from .models import (
    User, Project, Transaction, ProjectComment, ProjectUpdate,
    Achievement, VerificationCode, BackedProject, EcoWallet
)
from .database import engine
from .security import SECRET_KEY, ALGORITHM

admin_app = FastAPI()
admin = Admin(app=admin_app, engine=engine)

class AdminAuth(AuthenticationBackend):
    async def authenticate(self, request: Request) -> bool:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not admin"
            )

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("role") != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not admin"
                )
        except JWTError:
            return False

        return True

    async def login(self, request: Request) -> bool:
        return True

    async def logout(self, request: Request) -> bool:
        return True

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email, User.is_active, User.created_at]
    column_searchable_list = [User.name, User.email]
    column_sortable_list = [User.created_at]
    can_delete = True
    can_edit = True
    name = "User"
    name_plural = "Users"


class ProjectAdmin(ModelView, model=Project):
    column_list = [
        Project.id, Project.title, Project.category,
        Project.current_amount, Project.target_amount,
        Project.creator_id, Project.created_at, Project.end_date
    ]
    column_searchable_list = [Project.title, Project.category]
    column_sortable_list = [Project.created_at, Project.current_amount]
    can_delete = True
    can_edit = True
    name = "Project"
    name_plural = "Projects"


class TransactionAdmin(ModelView, model=Transaction):
    column_list = [
        Transaction.id, Transaction.user_id,
        Transaction.project_title, Transaction.amount,
        Transaction.status, Transaction.date
    ]
    column_sortable_list = [Transaction.date]
    name = "Transaction"
    name_plural = "Transactions"


class CommentAdmin(ModelView, model=ProjectComment):
    column_list = [
        ProjectComment.id, ProjectComment.project_id,
        ProjectComment.author_id, ProjectComment.date
    ]
    column_sortable_list = [ProjectComment.date]
    name = "Comment"
    name_plural = "Comments"


class UpdateAdmin(ModelView, model=ProjectUpdate):
    column_list = [
        ProjectUpdate.id, ProjectUpdate.project_id,
        ProjectUpdate.title, ProjectUpdate.date
    ]
    column_sortable_list = [ProjectUpdate.date]
    name = "Update"
    name_plural = "Project Updates"


class AchievementAdmin(ModelView, model=Achievement):
    column_list = [Achievement.id, Achievement.user_id, Achievement.title, Achievement.earned_at]
    column_sortable_list = [Achievement.earned_at]
    name = "Achievement"
    name_plural = "Achievements"


class VerificationCodeAdmin(ModelView, model=VerificationCode):
    column_list = [VerificationCode.id, VerificationCode.email, VerificationCode.code, VerificationCode.created_at, VerificationCode.expires_at]
    name = "Verification Code"
    name_plural = "Verification Codes"


class EcoWalletAdmin(ModelView, model=EcoWallet):
    column_list = [EcoWallet.user_id, EcoWallet.co2_saved, EcoWallet.trees_planted, EcoWallet.water_saved]
    can_create = False
    can_delete = False
    can_edit = False
    name = "Eco Wallet"
    name_plural = "Eco Wallets"


class BackedProjectAdmin(ModelView, model=BackedProject):
    column_list = [BackedProject.user_id, BackedProject.project_id]
    can_create = False
    can_delete = False
    can_edit = False
    name = "Backed Project"
    name_plural = "Backed Projects"


admin.add_view(UserAdmin)
admin.add_view(ProjectAdmin)
admin.add_view(TransactionAdmin)
admin.add_view(CommentAdmin)
admin.add_view(UpdateAdmin)
admin.add_view(AchievementAdmin)
admin.add_view(VerificationCodeAdmin)
admin.add_view(EcoWalletAdmin)
admin.add_view(BackedProjectAdmin)
