from datetime import datetime
from io import BytesIO
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from openpyxl import Workbook

from ..database import get_db
from ..dependencies import get_current_user, get_data_owner_id
from ..models import User, Member, ScoreRecord, LiveRoom

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/members")
def export_all_members(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_id = get_data_owner_id(user)
    members = db.query(Member).filter(Member.user_id == owner_id).order_by(Member.created_at).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "成员积分"
    ws.append(["姓名", "当前积分", "创建时间"])

    for m in members:
        score = m.records[0].balance_after if m.records else 0
        ws.append([m.name, score, m.created_at.strftime("%Y-%m-%d %H:%M:%S")])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=members.xlsx"},
    )


@router.get("/members/{member_id}/records")
def export_member_records(
    member_id: int,
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    room_id: Optional[int] = Query(None, description="直播间ID"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owner_id = get_data_owner_id(user)
    member = db.query(Member).filter(Member.id == member_id, Member.user_id == owner_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成员不存在")

    query = db.query(ScoreRecord).filter(ScoreRecord.member_id == member_id)

    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(ScoreRecord.created_at >= start)
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.filter(ScoreRecord.created_at <= end)
    if room_id is not None:
        query = query.filter(ScoreRecord.room_id == room_id)

    records = query.order_by(ScoreRecord.created_at.desc()).all()

    # Build room name lookup
    room_ids = {r.room_id for r in records if r.room_id}
    room_map = {}
    if room_ids:
        rooms = db.query(LiveRoom).filter(LiveRoom.id.in_(room_ids)).all()
        room_map = {rm.id: rm.name for rm in rooms}

    wb = Workbook()
    ws = wb.active
    ws.title = f"{member.name}-积分记录"
    ws.append(["时间", "变更", "原因", "变更后余额", "操作人", "直播间"])

    for r in records:
        ws.append([
            r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            r.change_amount,
            r.reason,
            r.balance_after,
            r.operator_name or "",
            room_map.get(r.room_id, "") if r.room_id else "",
        ])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename*=UTF-8''" + quote(f"{member.name}_records.xlsx")},
    )
