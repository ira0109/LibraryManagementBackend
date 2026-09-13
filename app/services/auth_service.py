from datetime import datetime, timedelta, timezone
from hmac import compare_digest
from typing import Optional
from fastapi import HTTPException, status
from passlib.context import CryptContext
import jwt

from app.config import settings
from app.models import User, RoleEnum
from app.schemas import UserRegister
from app.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def hash_password(self, password: str) -> str:
        # Truncate string to 72 characters to avoid bcrypt length limits
        return pwd_context.hash(password[:72])

    def verify_password(self, plain: str, hashed: str) -> bool:
        # Truncate string to 72 characters to avoid bcrypt length limits
        return pwd_context.verify(plain[:72], hashed)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def register_user(self, user_data: UserRegister) -> User:
        if user_data.role != RoleEnum.LIBRARIAN:
            raise HTTPException(
                status_code=403,
                detail="Only librarians can register new accounts. Members must use an existing account created by a librarian."
            )
        self.verify_admin_credential(user_data.admin_username, user_data.admin_password)

        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email is already registered")

        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=self.hash_password(user_data.password),
            role=RoleEnum.LIBRARIAN
        )
        return self.user_repo.create(user)

    def verify_admin_credential(self, admin_username: Optional[str], admin_password: Optional[str]) -> None:
        if (
            not settings.ADMIN_USERNAME
            or not settings.ADMIN_PASSWORD
            or not admin_username
            or not admin_password
            or not compare_digest(admin_username, settings.ADMIN_USERNAME)
            or not compare_digest(admin_password, settings.ADMIN_PASSWORD)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="A valid admin credential is required to create a librarian account."
            )

    def authenticate_user(self, email: str, password: str) -> str:
        user = self.user_repo.get_by_email(email)
        if not user or not self.verify_password(password, user.password_hash):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        return self.create_access_token(data={"sub": user.email})