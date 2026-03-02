from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import LoginRequest, TokenResponse, ChangePasswordRequest, UserInfoResponse
from ..auth import verify_password, hash_password, create_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = create_token(user.id)
    return TokenResponse(access_token=token, role=user.role, username=user.username)


@router.get("/me", response_model=UserInfoResponse)
def get_me(user: User = Depends(get_current_user)):
    return UserInfoResponse(id=user.id, username=user.username, role=user.role)


@router.post("/change-password")
def change_password(body: ChangePasswordRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(body.old_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误")
    if len(body.new_password) < 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于4位")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"message": "密码修改成功"}
