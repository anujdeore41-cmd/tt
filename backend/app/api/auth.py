from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.auth import security
from app.database import get_db
from app.models import User, Role
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.services.audit import record_audit

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

bearer_optional = HTTPBearer(auto_error=False)

# In-memory token blacklist for logout (tokens expire naturally via JWT exp)
_token_blacklist: set[str] = set()


def _get_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if role is None:
        descriptions = {
            "ADMIN": "Full administrative access",
            "FACULTY": "Faculty member access",
            "ACADEMIC_MANAGEMENT": "Read-only academic management access",
        }
        role = Role(name=name, description=descriptions.get(name, ""))
        db.add(role)
        db.flush()
    return role


@router.post("/register", response_model=UserOut, summary="Register a user (first user becomes ADMIN)")
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db),
             credentials=Depends(bearer_optional)):
    user_count = db.query(User).count()
    # Bootstrap: when no users exist the first account becomes ADMIN regardless of requested role.
    if user_count == 0:
        role_name = "ADMIN"
    else:
        # Only administrators may register additional users once the system is bootstrapped.
        admin = None
        if credentials is not None:
            claims = security.decode_access_token(credentials.credentials)
            if claims:
                admin = db.get(User, int(claims["sub"]))
        if admin is None or "ADMIN" not in admin.role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can register new users. Login as an administrator first.",
            )
        role_name = payload.role

    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=security.hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.flush()
    role = _get_role(db, role_name)
    from app.models import UserRole

    db.add(UserRole(user_id=user.id, role_id=role.id))
    record_audit(db, action="USER_REGISTERED", entity_type="user", entity_id=user.id,
                 new_value={"username": user.username, "role": role_name}, user=admin, request=request)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse, summary="Login with username/email and password")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.username)
    ).first()
    if user is None or not security.verify_password(payload.password, user.hashed_password):
        record_audit(db, action="LOGIN_FAILED", entity_type="user",
                     new_value={"username": payload.username}, request=request)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    token = security.create_access_token(str(user.id), {"username": user.username})
    record_audit(db, action="LOGIN", entity_type="user", entity_id=user.id, user=user, request=request)
    db.commit()
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/logout", summary="Logout (invalidates the current token server-side)")
def logout(credentials=Depends(bearer_optional)):
    if credentials is not None:
        _token_blacklist.add(credentials.credentials)
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserOut, summary="Get the current authenticated user")
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


def is_token_blacklisted(token: str) -> bool:
    return token in _token_blacklist
