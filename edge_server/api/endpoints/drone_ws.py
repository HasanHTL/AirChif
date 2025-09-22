from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from edge_server.utils.logger import logger

router = APIRouter()

@router.websocket("/ws/{mission_id}")
async def mission_ws(websocket: WebSocket, mission_id: int):
    await websocket.accept()
    logger.info(f"WebSocket connected for mission {mission_id}")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received from drone: {data}")
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
