from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, members, export, staff, rooms, records

app = FastAPI(title="积分管理系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(members.router)
app.include_router(export.router)
app.include_router(staff.router)
app.include_router(rooms.router)
app.include_router(records.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
