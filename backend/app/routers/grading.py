from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import db
from app.services.common import assert_shift_writable, audit, require_ticket, ticket_view

router = APIRouter(tags=["定级"])


class GradeLockIn(BaseModel):
    品级编号: int


@router.post("/定级/{ticket_id}")
def lock_grade(ticket_id: int, body: GradeLockIn):
    with db() as conn:
        ticket = require_ticket(conn, ticket_id)
        assert_shift_writable(conn, ticket["shift_id"])
        if ticket["status"] != "待定级":
            raise HTTPException(400, "仅待定级可锁价")
        grade = conn.execute("SELECT * FROM grades WHERE id=?", (body.品级编号,)).fetchone()
        if not grade:
            raise HTTPException(404, "品级不存在")
        if grade["unit_price"] <= 0:
            raise HTTPException(400, "单价无效")
        cur = conn.execute(
            """
            UPDATE tickets
            SET status='待结价', grade_id=?, locked_price=?
            WHERE id=? AND status='待定级'
            """,
            (grade["id"], grade["unit_price"], ticket_id),
        )
        if cur.rowcount != 1:
            raise HTTPException(400, "锁价未生效")
        audit(conn, "磅条", ticket_id, "定级锁价", f"{grade['category']}{grade['grade_name']}")
        return ticket_view(conn, ticket_id)
