# edge_server/api/router.py
from fastapi import APIRouter
from edge_server.api.endpoints import auth, journeys, missions, detections, drone_control

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(journeys.router, prefix="/journeys", tags=["journeys"])
api_router.include_router(missions.router, prefix="/missions", tags=["missions"])
api_router.include_router(detections.router, prefix="/detections", tags=["detections"])
api_router.include_router(drone_control.router, prefix="/drone", tags=["drone"])
