from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.api.deps import require_role
from app.utils.security import get_password_hash

router = APIRouter(prefix="/users", tags=["User Administration"])

@router.get("", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    return db.query(User).order_by(User.id.asc()).all()

@router.post("", response_model=UserOut)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        department=user_in.department,
        badge_number=user_in.badge_number,
        is_active=user_in.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.patch("/{id}", response_model=UserOut)
def update_user_status(
    id: int,
    user_up: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == admin.id and user_up.is_active is False:
        raise HTTPException(status_code=400, detail="Super Admin cannot deactivate their own account")

    for key, val in user_up.dict(exclude_unset=True).items():
        if key == "password" and val:
            user.hashed_password = get_password_hash(val)
        elif key != "password":
            setattr(user, key, val)

    db.commit()
    db.refresh(user)
    return user
