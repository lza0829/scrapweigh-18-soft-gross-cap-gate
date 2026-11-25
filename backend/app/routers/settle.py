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

router = APIRouter(tags=["结价"])


@router.post("/结价/{ticket_id}")
def settle(ticket_id: int):
    with db() as conn:
        ticket = require_ticket(conn, ticket_id)
        assert_shift_writable(conn, ticket["shift_id"])
        if ticket["status"] != "待结价":
            raise HTTPException(400, "仅待结价可结价")
        if ticket["locked_price"] is None:
            raise HTTPException(400, "尚未锁价")
        amount = round(float(ticket["net_kg"]) * float(ticket["locked_price"]), 2)
        cur = conn.execute(
            """
            UPDATE tickets
            SET status='已结价', amount=?, settled_at=?
            WHERE id=? AND status='待结价'
            """,
            (amount, now_str(), ticket_id),
        )
        if cur.rowcount != 1:
            raise HTTPException(400, "结价未生效")
        release_scale(conn, ticket["scale_id"])
        audit(conn, "磅条", ticket_id, "结算关账", str(amount))
        return ticket_view(conn, ticket_id)
