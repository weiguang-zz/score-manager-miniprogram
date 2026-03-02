from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, get_data_owner_id, require_editor
from ..models import User, Member, ScoreRecord, LiveRoom
from ..schemas import MemberCreate, MemberUpdate, MemberResponse, RecordCreate, RecordResponse

router = APIRouter(prefix="/api/members", tags=["members"])


def _get_current_score(member: Member) -> int:
    if member.records:
        return member.records[0].balance_after
    return 0


@router.get("", response_model=list[MemberResponse])
def list_members(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_id = get_data_owner_id(user)
    members = db.query(Member).filter(Member.user_id == owner_id).order_by(Member.created_at).all()
    return [
        MemberResponse(
            id=m.id,
            name=m.name,
            current_score=_get_current_score(m),
            created_at=m.created_at,
        )
        for m in members
    ]


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(body: MemberCreate, user: User = Depends(require_editor), db: Session = Depends(get_db)):
    owner_id = get_data_owner_id(user)
    member = Member(name=body.name, user_id=owner_id)
    db.add(member)
    db.flush()

    if body.initial_score != 0:
        record = ScoreRecord(
            member_id=member.id,
            change_amount=body.initial_score,
            reason="初始积分",
            balance_after=body.initial_score,
            operator_id=user.id,
            operator_name=user.username,
        )
        db.add(record)

    db.commit()
    db.refresh(member)
    return MemberResponse(
        id=member.id,
        name=member.name,
        current_score=body.initial_score,
        created_at=member.created_at,
    )


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, body: MemberUpdate, user: User = Depends(require_editor), db: Session = Depends(get_db)):
    owner_id = get_data_owner_id(user)
    member = db.query(Member).filter(Member.id == member_id, Member.user_id == owner_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成员不存在")
    member.name = body.name
    db.commit()
    db.refresh(member)
    return MemberResponse(
        id=member.id,
        name=member.name,
        current_score=_get_current_score(member),
        created_at=member.created_at,
    )


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, user: User = Depends(require_editor), db: Session = Depends(get_db)):
    owner_id = get_data_owner_id(user)
    member = db.query(Member).filter(Member.id == member_id, Member.user_id == owner_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成员不存在")
    db.delete(member)
    db.commit()


@router.get("/{member_id}/records", response_model=list[RecordResponse])
def list_records(member_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_id = get_data_owner_id(user)
    member = db.query(Member).filter(Member.id == member_id, Member.user_id == owner_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成员不存在")
    records = (
        db.query(ScoreRecord)
        .filter(ScoreRecord.member_id == member_id)
        .order_by(ScoreRecord.created_at.desc())
        .all()
    )
    return [
        RecordResponse(
            id=r.id,
            change_amount=r.change_amount,
            reason=r.reason,
            balance_after=r.balance_after,
            operator_name=r.operator_name,
            room_name=r.room.name if r.room else None,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.post("/{member_id}/records", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(member_id: int, body: RecordCreate, user: User = Depends(require_editor), db: Session = Depends(get_db)):
    owner_id = get_data_owner_id(user)
    member = db.query(Member).filter(Member.id == member_id, Member.user_id == owner_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成员不存在")

    current_score = _get_current_score(member)
    new_balance = current_score + body.change_amount

    record = ScoreRecord(
        member_id=member_id,
        change_amount=body.change_amount,
        reason=body.reason,
        balance_after=new_balance,
        operator_id=user.id,
        operator_name=user.username,
        room_id=body.room_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
