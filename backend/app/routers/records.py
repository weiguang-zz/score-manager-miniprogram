from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..dependencies import get_current_user, get_data_owner_id
from ..models import User, Member, ScoreRecord
from ..schemas import GlobalRecordItem, GlobalRecordResponse

router = APIRouter(prefix="/api/records", tags=["records"])


@router.get("", response_model=GlobalRecordResponse)
def list_global_records(
    date: str = Query(..., description="日期 YYYY-MM-DD"),
    room_id: int | None = Query(None, description="直播间ID"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owner_id = get_data_owner_id(user)

    day_start = datetime.strptime(date, "%Y-%m-%d")
    day_end = day_start.replace(hour=23, minute=59, second=59)

    # Get all member IDs belonging to this owner
    member_ids = [
        mid for (mid,) in db.query(Member.id).filter(Member.user_id == owner_id).all()
    ]

    if not member_ids:
        return GlobalRecordResponse(records=[], total_add=0, total_sub=0)

    query = (
        db.query(ScoreRecord)
        .options(joinedload(ScoreRecord.member), joinedload(ScoreRecord.room))
        .filter(
            ScoreRecord.member_id.in_(member_ids),
            ScoreRecord.created_at >= day_start,
            ScoreRecord.created_at <= day_end,
        )
    )

    if room_id is not None:
        query = query.filter(ScoreRecord.room_id == room_id)

    records = query.order_by(ScoreRecord.created_at.desc()).all()

    total_add = 0
    total_sub = 0
    items = []
    for r in records:
        if r.change_amount > 0:
            total_add += r.change_amount
        else:
            total_sub += r.change_amount
        items.append(GlobalRecordItem(
            id=r.id,
            member_name=r.member.name,
            change_amount=r.change_amount,
            reason=r.reason,
            balance_after=r.balance_after,
            operator_name=r.operator_name,
            room_name=r.room.name if r.room else None,
            created_at=r.created_at,
        ))

    return GlobalRecordResponse(records=items, total_add=total_add, total_sub=total_sub)
