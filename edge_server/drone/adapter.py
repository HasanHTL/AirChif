# edge_server/drone/adapter.py
import asyncio
import random
from datetime import datetime
from typing import Dict, Optional
from edge_server.utils.logger import logger
from edge_server.database.db import SessionLocal
from edge_server.database import crud

# This module provides a mock adapter that simulates a MAVLink drone.
# Later you can implement a real pymavlink adapter here and keep the same interface.

class MockMavAdapter:
    def __init__(self):
        self._tasks: Dict[int, asyncio.Task] = {}

    async def _run_sim(self, mission_id: int):
        logger.info("MockMavAdapter: starting simulation for mission %s", mission_id)
        db = SessionLocal()
        try:
            for i in range(60):  # simulate 60 steps (~60 seconds)
                lat = 48.2 + random.uniform(-0.001, 0.001)
                lon = 16.37 + random.uniform(-0.001, 0.001)
                telemetry = {
                    "type": "telemetry",
                    "mission_id": mission_id,
                    "lat": lat,
                    "lon": lon,
                    "alt": 10 + random.uniform(-1,1),
                    "battery": random.randint(50, 100),
                    "timestamp": datetime.utcnow().isoformat()
                }
                # If you want to propagate telemetry over WebSocket, import manager from endpoints.missions
                try:
                    from edge_server.api.endpoints.missions import manager
                    await manager.broadcast(mission_id, telemetry)
                except Exception:
                    pass

                # occasionally create detection
                if random.random() < 0.1:
                    detection_payload = type("D", (), {
                        "mission_id": mission_id,
                        "lat": lat,
                        "lon": lon,
                        "label": "plastic",
                        "score": round(random.uniform(0.7, 0.98), 3)
                    })()
                    # use crud.add_detection wrapper
                    det = crud.add_detection(db, detection_payload)
                    try:
                        from edge_server.api.endpoints.missions import manager
                        await manager.broadcast(mission_id, {
                            "type": "detection",
                            "lat": det.lat,
                            "lon": det.lon,
                            "label": det.label,
                            "score": det.score,
                            "timestamp": str(det.timestamp)
                        })
                    except Exception:
                        pass

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("MockMavAdapter: mission %s cancelled", mission_id)
        except Exception as e:
            logger.exception("MockMavAdapter: error for mission %s: %s", mission_id, e)
        finally:
            db.close()
            logger.info("MockMavAdapter: finished mission %s", mission_id)

    def start(self, mission_id: int):
        if mission_id in self._tasks:
            logger.info("MockMavAdapter: mission %s already running", mission_id)
            return
        loop = asyncio.get_event_loop()
        task = loop.create_task(self._run_sim(mission_id))
        self._tasks[mission_id] = task

    def stop(self, mission_id: int):
        t = self._tasks.pop(mission_id, None)
        if t:
            t.cancel()

    def send_command(self, mission_id: int, command: str, params=None):
        logger.info("MockMavAdapter: received command for mission %s: %s %s", mission_id, command, params)
        # simple stub: we can react to "rtl", "land", etc.
        if command == "land":
            self.stop(mission_id)

# Manager singleton
class DroneManager:
    def __init__(self):
        self.adapter = MockMavAdapter()

    def start_mission(self, mission_id: int):
        self.adapter.start(mission_id)

    def stop_mission(self, mission_id: int):
        self.adapter.stop(mission_id)

    def send_command(self, mission_id: int, command: str, params=None):
        self.adapter.send_command(mission_id, command, params=params)

drone_manager_singleton = DroneManager()
