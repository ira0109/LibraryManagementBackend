from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine, SessionLocal
from app.models import User, RoleEnum, AccountStatusEnum
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.controllers import (
    auth_controller,
    book_controller,
    member_controller,
    librarian_controller
)

# Auto-generate DB schema tables on startup
Base.metadata.create_all(bind=engine)


def bootstrap_admin() -> None:
    if not settings.ADMIN_PASSWORD:
        return

    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        existing_admin = user_repo.get_by_email(settings.ADMIN_USERNAME)
        if existing_admin:
            existing_admin.password_hash = AuthService(user_repo).hash_password(settings.ADMIN_PASSWORD)
            existing_admin.role = RoleEnum.LIBRARIAN
            existing_admin.status = AccountStatusEnum.ACTIVE
            db.commit()
            return

        admin = User(
            name="System Administrator",
            email=settings.ADMIN_USERNAME,
            password_hash=AuthService(user_repo).hash_password(settings.ADMIN_PASSWORD),
            role=RoleEnum.LIBRARIAN,
            status=AccountStatusEnum.ACTIVE,
        )
        user_repo.create(admin)
    finally:
        db.close()


bootstrap_admin()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade Library Management System built with Controller-Service-Repository architecture.",
    version="2.0.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register Controller Routers
app.include_router(auth_controller.router)
app.include_router(book_controller.router)
app.include_router(member_controller.router)
app.include_router(librarian_controller.router)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy", "system": settings.PROJECT_NAME}