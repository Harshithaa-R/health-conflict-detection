from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, Optional

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

DEMO_USERS = {
    "admin@karnataka.gov.in": {
        "email": "admin@karnataka.gov.in",
        "password": "admin123",
        "name": "District Admin",
        "role": "admin",
    },
    "reviewer@karnataka.gov.in": {
        "email": "reviewer@karnataka.gov.in",
        "password": "reviewer123",
        "name": "Clinical Reviewer",
        "role": "reviewer",
    },
    "analyst@karnataka.gov.in": {
        "email": "analyst@karnataka.gov.in",
        "password": "analyst123",
        "name": "Data Analyst",
        "role": "analyst",
    },
}

ACTIVE_TOKENS: Dict[str, Dict[str, str]] = {}


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    email: str
    name: str
    role: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


def _create_token_for_user(email: str) -> str:
    token = f"healthsync-{email}-{int(datetime.utcnow().timestamp())}"
    ACTIVE_TOKENS[token] = {
        "email": email,
        "expires_at": (datetime.utcnow() + timedelta(hours=12)).isoformat(),
    }
    return token


def _get_valid_token(credentials: Optional[HTTPAuthorizationCredentials]):
    if credentials is None or not credentials.scheme.lower() == "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = ACTIVE_TOKENS.get(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires_at = payload.get("expires_at")
    if expires_at and datetime.utcnow() > datetime.fromisoformat(expires_at):
        ACTIVE_TOKENS.pop(token, None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


@router.post("/login", response_model=TokenOut)
def login_user(payload: LoginRequest):
    email = str(payload.email).lower()
    user = DEMO_USERS.get(email)
    if not user or user["password"] != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = _create_token_for_user(user["email"])
    return TokenOut(
        access_token=token,
        user=UserOut(email=user["email"], name=user["name"], role=user["role"]),
    )


@router.get("/me", response_model=UserOut)
def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    payload = _get_valid_token(credentials)
    email = payload["email"]
    user = DEMO_USERS.get(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return UserOut(email=user["email"], name=user["name"], role=user["role"])


@router.post("/logout")
def logout_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    token = credentials.credentials if credentials else None
    if token:
        ACTIVE_TOKENS.pop(token, None)
    return {"message": "Logged out successfully"}


@router.get("/health")
def auth_health():
    return {"status": "ok", "demo_users": list(DEMO_USERS.keys())}
