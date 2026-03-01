from datetime import datetime
from pydantic import BaseModel


# Auth
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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


class RecordResponse(BaseModel):
    id: int
    change_amount: int
    reason: str
    balance_after: int
    created_at: datetime

    class Config:
        from_attributes = True
