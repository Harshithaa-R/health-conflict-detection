from datetime import datetime, timedelta, timezone
import secrets
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

# Local-development accounts only. Replace with a persistent user store and
# securely hashed passwords before deploying anywhere outside a demo environment.
DEMO_USERS = {
    "admin@karnataka.gov.in": {"email": "admin@karnataka.gov.in", "password": "admin123", "name": "District Admin", "role": "admin", "assigned_villages": []},
    "reviewer@karnataka.gov.in": {"email": "reviewer@karnataka.gov.in", "password": "reviewer123", "name": "Clinical Reviewer", "role": "reviewer", "assigned_villages": []},
    "analyst@karnataka.gov.in": {"email": "analyst@karnataka.gov.in", "password": "analyst123", "name": "Data Analyst", "role": "analyst", "assigned_villages": []},
    "chw@karnataka.gov.in": {"email": "chw@karnataka.gov.in", "password": "chw123", "name": "Community Health Worker", "role": "chw", "assigned_villages": []},
}
ACTIVE_TOKENS: Dict[str, Dict[str, str]] = {}


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    email: str
    name: str
    role: str
    assigned_villages: list[str] = []


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: str
    user: UserOut


def current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    session = ACTIVE_TOKENS.get(credentials.credentials)
    if not session:
        raise HTTPException(status_code=401, detail="Session is invalid or expired", headers={"WWW-Authenticate": "Bearer"})
    if datetime.now(timezone.utc) >= datetime.fromisoformat(session["expires_at"]):
        ACTIVE_TOKENS.pop(credentials.credentials, None)
        raise HTTPException(status_code=401, detail="Session is invalid or expired", headers={"WWW-Authenticate": "Bearer"})
    user = DEMO_USERS.get(session["email"])
    if user is None:
        raise HTTPException(status_code=401, detail="User is no longer active")
    return user


def require_roles(*roles: str):
    def role_dependency(user: dict = Depends(current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Your role is not permitted to perform this action")
        return user
    return role_dependency


def _user_out(user: dict) -> UserOut:
    return UserOut(email=user["email"], name=user["name"], role=user["role"], assigned_villages=user.get("assigned_villages", []))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest):
    email = payload.email.strip().lower()
    user = DEMO_USERS.get(email)
    if not user or not secrets.compare_digest(user["password"], payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    expiry = datetime.now(timezone.utc) + timedelta(hours=8)
    token = secrets.token_urlsafe(32)
    ACTIVE_TOKENS[token] = {"email": email, "expires_at": expiry.isoformat()}
    return TokenOut(access_token=token, expires_at=expiry.isoformat(), user=_user_out(user))


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(current_user)):
    return _user_out(user)


@router.post("/logout")
def logout(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if credentials:
        ACTIVE_TOKENS.pop(credentials.credentials, None)
    return {"message": "Logged out"}


@router.post("/password-reset")
def password_reset_request(payload: dict):
    # Deliberately do not reveal whether the account exists. Actual reset delivery
    # needs a trusted email/SMS provider and a one-time expiring reset token.
    return {"message": "If the account exists, password reset instructions will be sent."}
