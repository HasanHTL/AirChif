from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from edge_server.database import crud, schemas
from edge_server.api.deps import get_db_dep, get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.MissionOut)
def create_mission(mission_in: schemas.MissionCreate, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    return crud.create_mission(db, mission_in)

@router.get("/{mission_id}", response_model=schemas.MissionOut)
def get_mission(mission_id: int, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    mission = crud.get_mission(db, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission
