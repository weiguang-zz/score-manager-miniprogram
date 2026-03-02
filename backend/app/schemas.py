from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# Auth
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = ""
    username: str = ""


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserInfoResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


# Member
class MemberCreate(BaseModel):
    name: str
    initial_score: int = 0


class MemberUpdate(BaseModel):
    name: str


class MemberResponse(BaseModel):
    id: int
    name: str
    current_score: int
    created_at: datetime

    class Config:
        from_attributes = True


# Score Record
class RecordCreate(BaseModel):
    change_amount: int
    reason: str = ""
    room_id: Optional[int] = None


class RecordResponse(BaseModel):
    id: int
    change_amount: int
    reason: str
    balance_after: int
    operator_name: Optional[str] = None
    room_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Live Room
class RoomCreate(BaseModel):
    name: str


class RoomUpdate(BaseModel):
    name: str


class RoomResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# Global Records Query
class GlobalRecordItem(BaseModel):
    id: int
    member_name: str
    change_amount: int
    reason: str
    balance_after: int
    operator_name: Optional[str] = None
    room_name: Optional[str] = None
    created_at: datetime


class GlobalRecordResponse(BaseModel):
    records: List[GlobalRecordItem]
    total_add: int
    total_sub: int


# Staff
class StaffCreate(BaseModel):
    username: str
    password: str
    role: str = "staff_readonly"


class StaffUpdate(BaseModel):
    role: str


class StaffResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
