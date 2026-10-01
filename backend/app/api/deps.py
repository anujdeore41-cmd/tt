"""Shared FastAPI dependencies: authentication and role-based authorization."""
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.database import get_db
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)

ROLE_ADMIN = "ADMIN"
ROLE_FACULTY = "FACULTY"
ROLE_ACADEMIC = "ACADEMIC_MANAGEMENT"
ALL_ROLES = [ROLE_ADMIN, ROLE_FACULTY, ROLE_ACADEMIC]


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    request.state.user = user
    return user


def require_roles(*roles: str):
    """Dependency factory: allow only users holding one of the given roles."""

    def checker(user: User = Depends(get_current_user)) -> User:
        user_roles = set(user.role_names)
        if not user_roles & set(roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return user

    return checker


def require_admin(user: User = Depends(get_current_user)) -> User:
    return require_roles(ROLE_ADMIN)(user)


def require_staff(user: User = Depends(get_current_user)) -> User:
    """ADMIN or ACADEMIC_MANAGEMENT."""
    return require_roles(ROLE_ADMIN, ROLE_ACADEMIC)(user)


def require_any(user: User = Depends(get_current_user)) -> User:
    """Any authenticated role."""
    return require_roles(*ALL_ROLES)(user)
