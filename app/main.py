from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, get_db
from . import models
from sqlalchemy.orm import Session
from .auth.endpoints import router as auth_router
from .projects.endpoints import router as projects_router
from .users.endpoints import router as users_router
from .transaction.endpoints import router as transaction_router
from .comments.endpoints import router as comment_router
from sqladmin import Admin
from .admin import AdminAuth
from app.admin import UserAdmin, ProjectAdmin
from .security import SECRET_KEY, ALGORITHM
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(comment_router)
app.include_router(projects_router)
app.include_router(auth_router)
app.include_router(transaction_router)
app.include_router(users_router)

admin = Admin(app, engine, authentication_backend=AdminAuth(SECRET_KEY))

admin.add_view(UserAdmin)
admin.add_view(ProjectAdmin)


@app.get("/")
async def alive():
    return {"status": "alive"}
