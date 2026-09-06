from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.controllers import (
    auth_controller,
    book_controller,
    member_controller,
    librarian_controller
)

# Auto-generate DB schema tables on startup
Base.metadata.create_all(bind=engine)

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