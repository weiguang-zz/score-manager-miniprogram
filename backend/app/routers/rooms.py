from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, get_data_owner_id, require_admin
from ..models import User, LiveRoom
from ..schemas import RoomCreate, RoomUpdate, RoomResponse

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomResponse])
def list_rooms(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_id = get_data_owner_id(user)
    rooms = db.query(LiveRoom).filter(LiveRoom.user_id == owner_id).order_by(LiveRoom.created_at).all()
    return rooms


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(body: RoomCreate, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    owner_id = get_data_owner_id(user)
    room = LiveRoom(name=body.name, user_id=owner_id)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, body: RoomUpdate, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    owner_id = get_data_owner_id(user)
    room = db.query(LiveRoom).filter(LiveRoom.id == room_id, LiveRoom.user_id == owner_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="直播间不存在")
    room.name = body.name
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    owner_id = get_data_owner_id(user)
    room = db.query(LiveRoom).filter(LiveRoom.id == room_id, LiveRoom.user_id == owner_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="直播间不存在")
    db.delete(room)
    db.commit()
