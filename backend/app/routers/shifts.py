from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.db import db, rows_to_list, row_to_dict
from app.services.common import audit, now_str

router = APIRouter(tags=["班次"])

SHIFT_SQL = """
SELECT id AS 编号, business_day AS 营业日, name AS 班次名,
       status AS 状态, stamped_at AS 落印时间
FROM shifts
"""


class ShiftIn(BaseModel):
    营业日: str = Field(min_length=8)
    班次名: str = Field(min_length=1)


@router.get("/班次")
def list_shifts():
    with db() as conn:
        return rows_to_list(conn.execute(SHIFT_SQL + " ORDER BY id DESC").fetchall())


@router.post("/班次")
def create_shift(body: ShiftIn):
    with db() as conn:
        open_one = conn.execute("SELECT id FROM shifts WHERE status='未落印'").fetchone()
        if open_one:
            raise HTTPException(400, "仍有未落印班次，先落印再开新班")
        try:
            conn.execute(
                "INSERT INTO shifts(business_day, name, status) VALUES (?, ?, '未落印')",
                (body.营业日, body.班次名),
            )
        except Exception as e:
            raise HTTPException(400, f"开班失败: {e}")
        row = conn.execute(
            "SELECT id FROM shifts WHERE business_day=? AND name=?",
            (body.营业日, body.班次名),
        ).fetchone()
        audit(conn, "班次", row["id"], "开班", body.班次名)
        return row_to_dict(conn.execute(SHIFT_SQL + " WHERE id=?", (row["id"],)).fetchone())


@router.post("/班次/{shift_id}/落印")
def stamp_shift(shift_id: int):
    with db() as conn:
        shift = conn.execute("SELECT * FROM shifts WHERE id=?", (shift_id,)).fetchone()
        if not shift:
            raise HTTPException(404, "班次不存在")
        if shift["status"] == "已落印":
            raise HTTPException(400, "已落印")
        pending = conn.execute(
            """
            SELECT COUNT(*) AS c FROM tickets
            WHERE shift_id=? AND status IN ('待定级','待结价')
            """,
            (shift_id,),
        ).fetchone()["c"]
        if pending:
            raise HTTPException(400, f"仍有未结磅条 {pending}，禁止落印")
        conn.execute(
            "UPDATE shifts SET status='已落印', stamped_at=? WHERE id=? AND status='未落印'",
            (now_str(), shift_id),
        )
        audit(conn, "班次", shift_id, "落印", "")
        return row_to_dict(conn.execute(SHIFT_SQL + " WHERE id=?", (shift_id,)).fetchone())
