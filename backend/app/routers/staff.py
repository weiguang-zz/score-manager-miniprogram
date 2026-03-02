from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_admin
from ..models import User
from ..schemas import StaffCreate, StaffUpdate, StaffResponse
from ..auth import hash_password

router = APIRouter(prefix="/api/staff", tags=["staff"])

VALID_STAFF_ROLES = ("staff_readonly", "staff_editor")


@router.get("", response_model=list[StaffResponse])
def list_staff(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    staff_list = db.query(User).filter(User.admin_id == user.id).order_by(User.created_at).all()
    return staff_list


@router.post("", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
def create_staff(body: StaffCreate, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    if body.role not in VALID_STAFF_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的角色")
    if len(body.username) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名长度不能少于2位")
    if len(body.password) < 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码长度不能少于4位")

    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    staff = User(
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role,
        admin_id=user.id,
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@router.put("/{staff_id}", response_model=StaffResponse)
def update_staff(staff_id: int, body: StaffUpdate, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    if body.role not in VALID_STAFF_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的角色")

    staff = db.query(User).filter(User.id == staff_id, User.admin_id == user.id).first()
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="员工不存在")

    staff.role = body.role
    db.commit()
    db.refresh(staff)
    return staff


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    staff = db.query(User).filter(User.id == staff_id, User.admin_id == user.id).first()
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="员工不存在")
    db.delete(staff)
    db.commit()
