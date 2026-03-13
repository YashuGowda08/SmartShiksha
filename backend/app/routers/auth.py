"""Auth router — local email/password authentication with JWT."""
import base64
import json

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Dict, Any
from passlib.hash import bcrypt
from jose import jwt, JWTError

from app.database import get_db
from app.models import User
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()

# In-memory mobile auth handoff store used by Flutter desktop polling flow.
_MOBILE_SESSIONS: Dict[str, Dict[str, Any]] = {}


def serialize_user(user: User) -> dict:
    """Convert SQLAlchemy User to JSON-safe dict."""
    if not user:
        return None
    return {
        "id": str(user.id),
        "clerk_id": user.clerk_id,
        "name": user.name,
        "email": user.email,
        "student_class": user.student_class,
        "board": user.board,
        "language": user.language,
        "role": user.role,
        "onboarding_complete": user.onboarding_complete,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


def create_jwt(user_id: int, email: str) -> str:
    """Create a JWT token for a user."""
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=settings.JWT_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {e}")


def _decode_unverified_jwt_payload(token: str) -> dict:
    """Best-effort decode of JWT payload without signature verification.

    Used only as a development compatibility fallback for external identity tokens.
    """
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload_part = parts[1]
        padding = "=" * (-len(payload_part) % 4)
        decoded = base64.urlsafe_b64decode(payload_part + padding)
        data = json.loads(decoded.decode("utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


async def _resolve_user_from_token(token: str, db: AsyncSession) -> User:
    """Resolve local user from backend JWT first, else fallback to external JWT payload."""
    # Preferred path: backend-issued JWT.
    try:
        payload = decode_jwt(token)
        user_id = payload.get("sub")
        if user_id:
            result = await db.execute(select(User).where(User.id == int(user_id)))
            user = result.scalar_one_or_none()
            if user:
                return user
    except Exception:
        pass

    # Fallback path: external provider token (e.g., Clerk session token).
    payload = _decode_unverified_jwt_payload(token)
    ext_sub = str(payload.get("sub") or "").strip()
    ext_email = str(payload.get("email") or "").strip().lower()
    ext_name = (
        str(payload.get("name") or "").strip()
        or str(payload.get("given_name") or "").strip()
        or "Student"
    )

    if not ext_sub and not ext_email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Try by clerk_id.
    user = None
    if ext_sub:
        result = await db.execute(select(User).where(User.clerk_id == ext_sub))
        user = result.scalar_one_or_none()

    # Try by email.
    if user is None and ext_email:
        result = await db.execute(select(User).where(User.email == ext_email))
        user = result.scalar_one_or_none()

    # Create a local mirror user if missing.
    if user is None:
        email = ext_email or f"{ext_sub}@clerk.local"
        user = User(
            clerk_id=ext_sub or None,
            name=ext_name,
            email=email,
            password_hash=None,
            language="English",
            role="student",
            onboarding_complete=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    # Keep profile aligned when we do have user.
    updated = False
    if ext_sub and user.clerk_id != ext_sub:
        user.clerk_id = ext_sub
        updated = True
    if ext_name and user.name != ext_name:
        user.name = ext_name
        updated = True
    if ext_email and user.email != ext_email:
        user.email = ext_email
        updated = True
    if updated:
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)

    return user


async def get_current_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get current authenticated user from JWT."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")
    user = await _resolve_user_from_token(token, db)
    return serialize_user(user)


@router.post("/signup")
async def signup(data: dict, db: AsyncSession = Depends(get_db)):
    """Register a new user with email and password."""
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        raise HTTPException(status_code=400, detail="Name, email, and password are required")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # Check existing user
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    password_hash = bcrypt.hash(password)
    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        language="English",
        role="student",
        onboarding_complete=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_jwt(user.id, user.email)
    return {"token": token, "user": serialize_user(user)}


@router.post("/login")
async def login(data: dict, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not bcrypt.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_jwt(user.id, user.email)
    return {"token": token, "user": serialize_user(user)}


@router.post("/register")
async def register_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Register/fetch user from JWT token (for backward compatibility)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization.replace("Bearer ", "")
    user = await _resolve_user_from_token(token, db)
    return serialize_user(user)


@router.post("/onboarding")
async def complete_onboarding(
    data: dict,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Complete student onboarding with class, board, and language."""
    result = await db.execute(select(User).where(User.id == int(user["id"])))
    db_user = result.scalar_one_or_none()
    if db_user:
        db_user.student_class = data.get("student_class")
        db_user.board = data.get("board")
        db_user.language = data.get("language", "English")
        db_user.onboarding_complete = True
        db_user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_user)
        return serialize_user(db_user)
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return user


@router.patch("/me")
async def update_profile(
    data: dict,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile."""
    result = await db.execute(select(User).where(User.id == int(user["id"])))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if "name" in data and data["name"]:
        db_user.name = data["name"]
    if "language" in data and data["language"]:
        db_user.language = data["language"]
    if "avatar_url" in data:
        db_user.avatar_url = data["avatar_url"]
    db_user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(db_user)
    return serialize_user(db_user)


@router.post("/mobile/session")
async def create_mobile_session(
    data: dict,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Finalize browser auth and publish a backend token for a mobile/desktop device flow."""
    device_id = (data.get("device_id") or "").strip()
    if not device_id:
        raise HTTPException(status_code=400, detail="device_id is required")

    user = None

    # Prefer an already-valid backend JWT if present.
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        try:
            payload = decode_jwt(token)
            user_id = payload.get("sub")
            if user_id:
                result = await db.execute(select(User).where(User.id == int(user_id)))
                user = result.scalar_one_or_none()
        except Exception:
            user = None

    # Development fallback: create a local desktop user when browser token is not a backend JWT.
    if user is None:
        fallback_email = "desktop.mobile.auth@smartshiksha.local"
        result = await db.execute(select(User).where(User.email == fallback_email))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                name="Desktop User",
                email=fallback_email,
                password_hash=None,
                language="English",
                role="student",
                onboarding_complete=False,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

    app_token = create_jwt(user.id, user.email)
    _MOBILE_SESSIONS[device_id] = {
        "status": "ready",
        "token": app_token,
        "user_id": str(user.id),
        "updated_at": datetime.utcnow().isoformat(),
    }
    return {"status": "ready"}


@router.get("/mobile/session/{device_id}")
async def get_mobile_session(device_id: str):
    """Poll endpoint used by Flutter app while waiting for browser auth completion."""
    session = _MOBILE_SESSIONS.get(device_id)
    if not session:
        return {"status": "pending"}
    return session
