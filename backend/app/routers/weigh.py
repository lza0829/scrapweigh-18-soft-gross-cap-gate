from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.db import db, rows_to_list
from app.services.common import (
    TICKET_SELECT,
    audit,
    current_shift,
    get_setting,
    next_serial,
    now_str,
    occupy_scale,
    ticket_view,
)

router = APIRouter(tags=["过磅"])


class WeighIn(BaseModel):
    地磅编号: int
    回收点编号: int | None = None
    毛重: float = Field(gt=0)
    皮重: float = Field(ge=0)
    扣杂: float | None = None
    备注: str = ""


@router.get("/过磅")
def list_open_weighs():
    with db() as conn:
        return rows_to_list(conn.execute(
            TICKET_SELECT + " WHERE t.status IN ('待定级','待结价') ORDER BY t.id DESC LIMIT 100"
        ).fetchall())


@router.post("/过磅")
def admit(body: WeighIn):
    with db() as conn:
        shift = current_shift(conn)
        scale = conn.execute("SELECT * FROM scales WHERE id=?", (body.地磅编号,)).fetchone()
        if not scale:
            raise HTTPException(404, "地磅不存在")
        site = conn.execute("SELECT * FROM sites WHERE id=?", (scale["site_id"],)).fetchone()
        if not site:
            raise HTTPException(400, "回收点不存在")
        if body.回收点编号 is not None and body.回收点编号 != site["id"]:
            raise HTTPException(400, "地磅不属于该回收点")
        if site["status"] != "营业中":
            raise HTTPException(400, f"回收点{site['status']}，不能过磅")
        if body.皮重 >= body.毛重:
            raise HTTPException(400, "皮重须小于毛重")
        try:
            cap = float(get_setting(conn, "毛重软上限", "40000"))
        except ValueError:
            cap = 40000.0
        if body.毛重 > cap:
            raise HTTPException(400, "毛重超过软上限")
        if body.扣杂 is None:
            try:
                deduct = float(get_setting(conn, "扣杂默认", "0"))
            except ValueError:
                deduct = 0.0
        else:
            deduct = body.扣杂
        if deduct < 0:
            raise HTTPException(400, "扣杂不能为负")
        net = round(body.毛重 - body.皮重 - deduct, 3)
        if net <= 0:
            raise HTTPException(400, "净重须大于零")
        occupy_scale(conn, scale["id"])
        serial = next_serial(conn)
        conn.execute(
            """
            INSERT INTO tickets(
              serial, site_id, scale_id, shift_id, status,
              gross_kg, tare_kg, deduct_kg, net_kg, note, created_at
            ) VALUES (?, ?, ?, ?, '待定级', ?, ?, ?, ?, ?, ?)
            """,
            (
                serial, site["id"], scale["id"], shift["id"],
                body.毛重, body.皮重, deduct, net, body.备注, now_str(),
            ),
        )
        row = conn.execute("SELECT id FROM tickets WHERE serial=?", (serial,)).fetchone()
        audit(conn, "磅条", row["id"], "过磅入站", serial)
        return ticket_view(conn, row["id"])
