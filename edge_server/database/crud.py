# edge_server/database/crud.py
from sqlalchemy.orm import Session
from edge_server.database import models, schemas
from edge_server.utils.security import get_password_hash

# User
def create_user(db: Session, user_in: schemas.UserCreate):
    user = models.User(email=user_in.email, hashed_password=get_password_hash(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).get(user_id)

# Journey
def create_journey(db: Session, user_id: int, journey_in: schemas.JourneyCreate):
    journey = models.Journey(name=journey_in.name, description=journey_in.description, owner_id=user_id)
    db.add(journey)
    db.flush()
    for i, wp in enumerate(journey_in.points):
        waypoint = models.Waypoint(seq=wp.seq, lat=wp.lat, lon=wp.lon, alt=wp.alt, journey_id=journey.id)
        db.add(waypoint)
    db.commit()
    db.refresh(journey)
    return journey

def get_journeys(db: Session, user_id: int):
    return db.query(models.Journey).filter(models.Journey.owner_id == user_id).all()

def get_journey(db: Session, journey_id: int):
    return db.query(models.Journey).get(journey_id)

# Mission
def create_mission(db: Session, mission_in: schemas.MissionCreate):
    mission = models.Mission(journey_id=mission_in.journey_id)
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission

def get_mission(db: Session, mission_id: int):
    return db.query(models.Mission).get(mission_id)

# Detection
def create_detection(db: Session, det_in: schemas.DetectionCreate):
    det = models.Detection(**det_in.dict())
    db.add(det)
    db.commit()
    db.refresh(det)
    return det
