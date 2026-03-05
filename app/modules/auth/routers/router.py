from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import auth_rate_limit, get_current_user
from app.modules.auth.repositories import UserProfile
from app.modules.auth.schemas.dto import (
    AuthResponse,
    LoginRequest,
    ProfileUpdateRequest,
    RefreshRequest,
    RegisterRequest,
    UserRead,
)
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
async def me(current_user: UserProfile = Depends(get_current_user)) -> UserRead:
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role=current_user.role,
        created_at=current_user.created_at,
    )


@router.patch("/profile", response_model=UserRead)
async def update_profile(
    payload: ProfileUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    return await DatabaseAuthService(db).update_profile(current_user.id, payload)