from fastapi import FastAPI
from edge_server.config import settings
from edge_server.database.db import Base, engine
from edge_server.api.endpoints import auth, journeys, missions, detections, drone_ws

# DB erstellen
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(journeys.router, prefix=f"{settings.API_V1_STR}/journeys", tags=["journeys"])
app.include_router(missions.router, prefix=f"{settings.API_V1_STR}/missions", tags=["missions"])
app.include_router(detections.router, prefix=f"{settings.API_V1_STR}/detections", tags=["detections"])
app.include_router(drone_ws.router, prefix=f"{settings.API_V1_STR}/missions", tags=["websocket"])
