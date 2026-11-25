from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.db import db
from app.services.common import (
    assert_shift_writable,
    audit,
    now_str,
    release_scale,
    require_ticket,
    ticket_view,
)

router = APIRouter(tags=["销单"])


@router.post("/销单/{ticket_id}")
def void_ticket(ticket_id: int):
    with db() as conn:
        ticket = require_ticket(conn, ticket_id)
        assert_shift_writable(conn, ticket["shift_id"])
        if ticket["status"] not in ("待定级", "待结价"):
            raise HTTPException(400, "仅待定级或待结价可销单")
        cur = conn.execute(
            """
            UPDATE tickets
            SET status='已销', voided_at=?
            WHERE id=? AND status IN ('待定级','待结价')
            """,
            (now_str(), ticket_id),
        )
        if cur.rowcount != 1:
            raise HTTPException(400, "销单未生效")
        release_scale(conn, ticket["scale_id"])
        audit(conn, "磅条", ticket_id, "销单", ticket["serial"])
        return ticket_view(conn, ticket_id)
