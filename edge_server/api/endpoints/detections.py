from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from edge_server.database import crud, schemas
from edge_server.api.deps import get_db_dep, get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.DetectionOut)
def create_detection(det_in: schemas.DetectionCreate, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    return crud.create_detection(db, det_in)
