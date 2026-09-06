from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import RequestCreate, RequestResponse, MemberDashboardResponse
from app.models import User, RoleEnum
from app.dependencies import require_role
from app.repositories.book_repository import BookRepository
from app.repositories.request_repository import RequestRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.member_service import MemberService

router = APIRouter(prefix="/api/v1/member", tags=["Member Operations"])

def get_member_service(db: Session = Depends(get_db)) -> MemberService:
    return MemberService(
        BookRepository(db), RequestRepository(db), TransactionRepository(db), UserRepository(db)
    )

@router.post("/request", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
def submit_request(
    req_data: RequestCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role(RoleEnum.MEMBER)),
    service: MemberService = Depends(get_member_service)
):
    return service.submit_request(req_data, current_user, background_tasks)

@router.get("/dashboard", response_model=MemberDashboardResponse)
def get_dashboard(
    current_user: User = Depends(require_role(RoleEnum.MEMBER)),
    service: MemberService = Depends(get_member_service)
):
    return service.get_dashboard_data(current_user)