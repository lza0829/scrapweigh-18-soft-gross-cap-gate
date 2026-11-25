from __future__ import annotations
from fastapi import APIRouter
from app.db import db, rows_to_list, row_to_dict

router = APIRouter(tags=["总览"])

TICKET_STATUS = ("待定级", "待结价", "已结价", "已销")


@router.get("/总览")
def overview():
    with db() as conn:
        shift = conn.execute(
            """
            SELECT id AS 编号, business_day AS 营业日, name AS 班次名,
                   status AS 状态, stamped_at AS 落印时间
            FROM shifts ORDER BY id DESC LIMIT 1
            """
        ).fetchone()
        counts = {}
        for name in TICKET_STATUS:
            counts[name] = conn.execute(
                "SELECT COUNT(*) AS c FROM tickets WHERE status=?", (name,)
            ).fetchone()["c"]
        scales = rows_to_list(conn.execute(
            """
            SELECT sc.id AS 编号, sc.code AS 地磅, sc.status AS 状态, st.name AS 回收点, st.status AS 回收点状态
            FROM scales sc JOIN sites st ON st.id = sc.site_id
            ORDER BY st.id, sc.id
            """
        ).fetchall())
        return {"班次": row_to_dict(shift), "分布": counts, "地磅": scales}
