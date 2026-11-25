from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.db import db, rows_to_list, row_to_dict
from app.services.common import audit

router = APIRouter(tags=["品级"])

GRADE_SQL = """
SELECT id AS 编号, category AS 品类, grade_name AS 品级名, unit_price AS 单价
FROM grades
"""


class GradeIn(BaseModel):
    品类: str = Field(min_length=1)
    品级名: str = Field(min_length=1)
    单价: float = Field(gt=0)


@router.get("/品级")
def list_grades():
    with db() as conn:
        return rows_to_list(conn.execute(GRADE_SQL + " ORDER BY category, grade_name").fetchall())


@router.post("/品级")
def save_grade(body: GradeIn):
    with db() as conn:
        exist = conn.execute(
            "SELECT id FROM grades WHERE category=? AND grade_name=?",
            (body.品类, body.品级名),
        ).fetchone()
        if exist:
            conn.execute(
                "UPDATE grades SET unit_price=? WHERE id=?",
                (body.单价, exist["id"]),
            )
            gid = exist["id"]
            action = "改价"
        else:
            conn.execute(
                "INSERT INTO grades(category, grade_name, unit_price) VALUES (?, ?, ?)",
                (body.品类, body.品级名, body.单价),
            )
            gid = conn.execute(
                "SELECT id FROM grades WHERE category=? AND grade_name=?",
                (body.品类, body.品级名),
            ).fetchone()["id"]
            action = "新建"
        audit(conn, "品级", gid, action, f"{body.品类}{body.品级名}")
        return row_to_dict(conn.execute(GRADE_SQL + " WHERE id=?", (gid,)).fetchone())
