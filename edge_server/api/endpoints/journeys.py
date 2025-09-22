# edge_server/api/endpoints/journeys.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from typing import List, Dict, Any
from datetime import datetime

from edge_server.api.deps import get_db_dep, get_current_user
from edge_server.database import schemas
from edge_server.database.models import Journey, Waypoint
from edge_server.utils.logger import logger

router = APIRouter()


def _waypoint_column_name():
    """
    Return the column name used for waypoint sequence in the current models.
    Tries 'seq' first, then 'sequence'. Falls back to 'seq'.
    """
    if hasattr(Waypoint, "seq"):
        return "seq"
    if hasattr(Waypoint, "sequence"):
        return "sequence"
    return "seq"


@router.post("/", response_model=schemas.JourneyOut, status_code=status.HTTP_201_CREATED)
def create_journey(payload: schemas.JourneyCreate, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    # Basic validation of points
    if not payload.points or len(payload.points) < 2:
        raise HTTPException(status_code=400, detail="A journey requires at least 2 points.")

    # create Journey
    j = Journey(
        name=payload.name,
        description=getattr(payload, "description", None) or None,
        owner_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(j)
    db.flush()  # get j.id without commit

    seq_col = _waypoint_column_name()
    for i, p in enumerate(payload.points):
        lat = getattr(p, "lat", None)
        lon = getattr(p, "lon", None)
        alt = getattr(p, "alt", None) if hasattr(p, "alt") else None
        seq_val = getattr(p, "sequence", None) if hasattr(p, "sequence") else getattr(p, "seq", i)

        if lat is None or lon is None:
            raise HTTPException(status_code=400, detail=f"Waypoint #{i} missing lat/lon")

        wp_kwargs = {"journey_id": j.id, "lat": float(lat), "lon": float(lon)}
        # set the correct sequence field depending on model
        wp_kwargs[seq_col] = int(seq_val) if seq_val is not None else i
        # also include alt if model has it
        if hasattr(Waypoint, "alt"):
            wp_kwargs["alt"] = alt

        wp = Waypoint(**wp_kwargs)
        db.add(wp)

    db.commit()
    db.refresh(j)

    # eager-load waypoints
    j = db.query(Journey).options(selectinload(Journey.waypoints)).get(j.id)

    # Build response in a stable shape (seq field used for consistency)
    waypoints_out = []
    for idx, wp in enumerate(sorted(j.waypoints, key=lambda w: getattr(w, "seq", getattr(w, "sequence", idx)))):
        seq_value = getattr(wp, "seq", None)
        if seq_value is None:
            seq_value = getattr(wp, "sequence", idx)
        waypoints_out.append({
            "id": wp.id,
            "seq": seq_value,
            "lat": wp.lat,
            "lon": wp.lon,
            "alt": getattr(wp, "alt", None)
        })

    response = {
        "id": j.id,
        "name": j.name,
        "description": j.description,
        "owner_id": j.owner_id,
        "created_at": j.created_at,
        "waypoints": waypoints_out
    }
    return response


@router.get("/", response_model=List[schemas.JourneyOut])
def list_journeys(db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    qs = db.query(Journey).filter(Journey.owner_id == current_user.id).options(selectinload(Journey.waypoints)).all()
    out = []
    for j in qs:
        waypoints_out = []
        for idx, wp in enumerate(sorted(j.waypoints, key=lambda w: getattr(w, "seq", getattr(w, "sequence", idx)))):
            seq_value = getattr(wp, "seq", None)
            if seq_value is None:
                seq_value = getattr(wp, "sequence", idx)
            waypoints_out.append({
                "id": wp.id,
                "seq": seq_value,
                "lat": wp.lat,
                "lon": wp.lon,
                "alt": getattr(wp, "alt", None)
            })
        out.append({
            "id": j.id,
            "name": j.name,
            "description": j.description,
            "owner_id": j.owner_id,
            "created_at": j.created_at,
            "waypoints": waypoints_out
        })
    return out


@router.get("/{journey_id}", response_model=schemas.JourneyOut)
def get_journey(journey_id: int, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    j = db.query(Journey).options(selectinload(Journey.waypoints)).get(journey_id)
    if not j or j.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Journey not found")
    waypoints_out = []
    for idx, wp in enumerate(sorted(j.waypoints, key=lambda w: getattr(w, "seq", getattr(w, "sequence", idx)))):
        seq_value = getattr(wp, "seq", None)
        if seq_value is None:
            seq_value = getattr(wp, "sequence", idx)
        waypoints_out.append({
            "id": wp.id,
            "seq": seq_value,
            "lat": wp.lat,
            "lon": wp.lon,
            "alt": getattr(wp, "alt", None)
        })
    return {
        "id": j.id,
        "name": j.name,
        "description": j.description,
        "owner_id": j.owner_id,
        "created_at": j.created_at,
        "waypoints": waypoints_out
    }


@router.delete("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journey(journey_id: int, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    j = db.query(Journey).get(journey_id)
    if not j or j.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Journey not found")
    db.delete(j)
    db.commit()
    return {"detail": "deleted"}


@router.get("/{journey_id}/export")
def export_journey_geojson(journey_id: int, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    j = db.query(Journey).options(selectinload(Journey.waypoints)).get(journey_id)
    if not j or j.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Journey not found")
    coords = []
    for idx, wp in enumerate(sorted(j.waypoints, key=lambda w: getattr(w, "seq", getattr(w, "sequence", idx)))):
        coords.append([wp.lon, wp.lat])
    geojson = {
        "type": "Feature",
        "properties": {"name": j.name, "description": j.description},
        "geometry": {"type": "LineString", "coordinates": coords}
    }
    return geojson
