# edge_server/database/schemas.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        orm_mode = True

# Waypoint
class WaypointBase(BaseModel):
    seq: int
    lat: float
    lon: float
    alt: Optional[float] = None

class WaypointCreate(WaypointBase):
    pass

class WaypointOut(WaypointBase):
    id: int
    class Config:
        orm_mode = True

# Journey
class JourneyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    points: List[WaypointCreate]

class JourneyOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    created_at: datetime
    waypoints: List[WaypointOut]
    class Config:
        orm_mode = True

# Mission
class MissionCreate(BaseModel):
    journey_id: int

class MissionOut(BaseModel):
    id: int
    journey_id: int
    status: str
    started_at: datetime
    class Config:
        orm_mode = True

# Detection
class DetectionCreate(BaseModel):
    mission_id: int
    lat: float
    lon: float
    label: str
    score: Optional[float] = None

class DetectionOut(DetectionCreate):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True
