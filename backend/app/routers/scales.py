from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.db import db, rows_to_list, row_to_dict
from app.services.common import audit

router = APIRouter(tags=["地磅"])

SCALE_SQL = """
SELECT sc.id AS 编号, sc.code AS 地磅, sc.status AS 状态, sc.note AS 备注,
       st.id AS 回收点编号, st.name AS 回收点, st.status AS 回收点状态
FROM scales sc JOIN sites st ON st.id = sc.site_id
"""


class ScaleIn(BaseModel):
    回收点编号: int
    地磅: str = Field(min_length=1)
    备注: str = ""


class StatusIn(BaseModel):
    状态: str


def _scale(conn, scale_id: int):
    return row_to_dict(conn.execute(SCALE_SQL + " WHERE sc.id=?", (scale_id,)).fetchone())


@router.get("/地磅")
def list_scales():
    with db() as conn:
        return rows_to_list(conn.execute(SCALE_SQL + " ORDER BY st.id, sc.id").fetchall())


@router.post("/地磅")
def create_scale(body: ScaleIn):
    with db() as conn:
        site = conn.execute("SELECT * FROM sites WHERE id=?", (body.回收点编号,)).fetchone()
        if not site:
            raise HTTPException(404, "回收点不存在")
        if site["status"] == "已注销":
            raise HTTPException(400, "已注销回收点不能新增地磅")
        try:
            conn.execute(
                "INSERT INTO scales(site_id, code, status, note) VALUES (?, ?, '空闲', ?)",
                (body.回收点编号, body.地磅, body.备注),
            )
        except Exception as e:
            raise HTTPException(400, f"创建失败: {e}")
        row = conn.execute(
            "SELECT id FROM scales WHERE site_id=? AND code=?",
            (body.回收点编号, body.地磅),
        ).fetchone()
        audit(conn, "地磅", row["id"], "新建", body.地磅)
        return _scale(conn, row["id"])


@router.post("/地磅/{scale_id}/状态")
def set_scale_status(scale_id: int, body: StatusIn):
    if body.状态 not in ("空闲", "故障"):
        raise HTTPException(400, "只能改为空闲或故障")
    with db() as conn:
        row = conn.execute("SELECT * FROM scales WHERE id=?", (scale_id,)).fetchone()
        if not row:
            raise HTTPException(404, "地磅不存在")
        if row["status"] == "占用":
            raise HTTPException(400, "占用中的地磅不能改状态")
        if body.状态 == "故障" and row["status"] != "空闲":
            raise HTTPException(400, "仅空闲可标故障")
        if body.状态 == "空闲" and row["status"] != "故障":
            raise HTTPException(400, "仅故障可恢复空闲")
        conn.execute("UPDATE scales SET status=? WHERE id=?", (body.状态, scale_id))
        audit(conn, "地磅", scale_id, "改状态", body.状态)
        return _scale(conn, scale_id)
