from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import auth_rate_limit, get_current_user
from app.modules.auth.models.entity import User
from app.modules.auth.schemas.dto import AuthResponse, LoginRequest, RefreshRequest, RegisterRequest, UserRead
from app.modules.auth.services.service import DatabaseAuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(auth_rate_limit("register")),
) -> AuthResponse:
    return await DatabaseAuthService(db).register(payload)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(auth_rate_limit("login")),
) -> AuthResponse:
    return await DatabaseAuthService(db).login(payload)


@router.post("/refresh", response_model=AuthResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    return await DatabaseAuthService(db).refresh(payload.refresh_token)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        created_at=current_user.created_at,
    )