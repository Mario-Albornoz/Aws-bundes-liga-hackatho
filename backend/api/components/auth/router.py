import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from passlib.context import CryptContext

from api.components.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_token,
)
from api.components.auth.models import (
    AccessTokenResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from api.components.auth.token_cache import (
    get_refresh_token_user_id,
    revoke_refresh_token,
    store_refresh_token,
)
from api.database.DatabaseManager import database_manager

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest) -> TokenResponse:
    try:
        user = await database_manager.create_user(
            username=body.username,
            name=body.name,
            last_name=body.last_name,
            password_hash=_hash_password(body.password),
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id)
    store_refresh_token(hash_token(refresh_token), user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        username=user.username,
        name=user.name,
        last_name=user.last_name,
        balance=user.balance,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    user = await database_manager.get_user_by_username(body.username)
    if user is None or not _verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id)
    store_refresh_token(hash_token(refresh_token), user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        username=user.username,
        name=user.name,
        last_name=user.last_name,
        balance=user.balance,
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(body: RefreshRequest) -> AccessTokenResponse:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )

    try:
        payload = decode_refresh_token(body.refresh_token)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise credentials_error

    stored_user_id = get_refresh_token_user_id(hash_token(body.refresh_token))
    if stored_user_id is None or stored_user_id != user_id:
        raise credentials_error

    user = await database_manager.get_user_by_id(user_id)
    if user is None:
        raise credentials_error

    return AccessTokenResponse(access_token=create_access_token(user.id, user.username))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: LogoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> None:
    try:
        decode_access_token(credentials.credentials)
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    revoke_refresh_token(hash_token(body.refresh_token))


@router.get("/me")
async def me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await database_manager.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "user_id": user.id,
        "username": user.username,
        "name": user.name,
        "last_name": user.last_name,
        "balance": user.balance,
    }
