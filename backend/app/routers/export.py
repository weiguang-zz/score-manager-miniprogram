from io import BytesIO
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from openpyxl import Workbook

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Member, ScoreRecord

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/members")
def export_all_members(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    members = db.query(Member).filter(Member.user_id == user.id).order_by(Member.created_at).all()

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
def export_member_records(member_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id, Member.user_id == user.id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成员不存在")

    records = (
        db.query(ScoreRecord)
        .filter(ScoreRecord.member_id == member_id)
        .order_by(ScoreRecord.created_at.desc())
        .all()
    )

    wb = Workbook()
    ws = wb.active
    ws.title = f"{member.name}-积分记录"
    ws.append(["时间", "变更", "原因", "变更后余额"])

    for r in records:
        ws.append([
            r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            r.change_amount,
            r.reason,
            r.balance_after,
        ])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename*=UTF-8''" + quote(f"{member.name}_records.xlsx")},
    )
