# edge_server/api/deps.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from edge_server.database.db import get_db
from edge_server.database import crud
from edge_server.utils.security import decode_token

def get_db_dep():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db_dep)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = crud.get_user(db, int(payload.get("sub")))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
