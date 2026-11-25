from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.db import db, rows_to_list
from app.db import TICKET_STATUSES
from app.services.common import TICKET_SELECT

router = APIRouter(tags=["磅条"])


@router.get("/磅条")
def list_tickets(状态: str | None = None):
    if 状态 is not None and 状态 not in TICKET_STATUSES:
        raise HTTPException(400, "状态无效")
    with db() as conn:
        if 状态:
            rows = conn.execute(
                TICKET_SELECT + " WHERE t.status=? ORDER BY t.id DESC LIMIT 200",
                (状态,),
            ).fetchall()
        else:
            rows = conn.execute(TICKET_SELECT + " ORDER BY t.id DESC LIMIT 200").fetchall()
        return rows_to_list(rows)
