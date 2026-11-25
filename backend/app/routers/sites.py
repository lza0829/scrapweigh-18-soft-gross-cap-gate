from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.db import db, rows_to_list, row_to_dict
from app.services.common import audit

router = APIRouter(tags=["回收点"])

SITE_STATUS = ("营业中", "停收", "已注销")


class SiteIn(BaseModel):
    名称: str = Field(min_length=1)
    地址: str = ""


class StatusIn(BaseModel):
    状态: str


def _site(conn, site_id: int):
    row = conn.execute(
        "SELECT id AS 编号, name AS 名称, status AS 状态, address AS 地址 FROM sites WHERE id=?",
        (site_id,),
    ).fetchone()
    return row_to_dict(row)


@router.get("/回收点")
def list_sites():
    with db() as conn:
        return rows_to_list(conn.execute(
            "SELECT id AS 编号, name AS 名称, status AS 状态, address AS 地址 FROM sites ORDER BY id"
        ).fetchall())


@router.post("/回收点")
def create_site(body: SiteIn):
    with db() as conn:
        try:
            conn.execute(
                "INSERT INTO sites(name, status, address) VALUES (?, '营业中', ?)",
                (body.名称, body.地址),
            )
        except Exception as e:
            raise HTTPException(400, f"创建失败: {e}")
        row = conn.execute("SELECT id FROM sites WHERE name=?", (body.名称,)).fetchone()
        audit(conn, "回收点", row["id"], "新建", body.名称)
        return _site(conn, row["id"])


@router.post("/回收点/{site_id}/状态")
def set_site_status(site_id: int, body: StatusIn):
    if body.状态 not in SITE_STATUS:
        raise HTTPException(400, "状态仅允许营业中、停收或已注销")
    with db() as conn:
        cur = conn.execute("UPDATE sites SET status=? WHERE id=?", (body.状态, site_id))
        if cur.rowcount == 0:
            raise HTTPException(404, "回收点不存在")
        audit(conn, "回收点", site_id, "改状态", body.状态)
        return _site(conn, site_id)
