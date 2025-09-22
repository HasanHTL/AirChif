# edge_server/api/endpoints/drone_control.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from edge_server.api.deps import get_db_dep, get_current_user
from edge_server.drone.adapter import drone_manager_singleton
from edge_server.database import crud

router = APIRouter()

@router.post("/{mission_id}/command")
def send_command(mission_id: int, body: Dict, db: Session = Depends(get_db_dep), current_user = Depends(get_current_user)):
    cmd = body.get("command")
    if not cmd:
        raise HTTPException(status_code=400, detail="Missing command")
    # For now, we just forward to manager (mock)
    drone_manager_singleton.send_command(mission_id, cmd, params=body.get("params"))
    return {"detail": "Command forwarded"}
