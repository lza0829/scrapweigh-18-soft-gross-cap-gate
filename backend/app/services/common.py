from __future__ import annotations
from datetime import datetime
from fastapi import HTTPException

TICKET_SELECT = """
SELECT t.id AS 编号,
       t.serial AS 磅条号,
       t.site_id AS 回收点编号,
       st.name AS 回收点,
       t.scale_id AS 地磅编号,
       sc.code AS 地磅,
       sc.status AS 地磅状态,
       t.shift_id AS 班次编号,
       sh.business_day AS 营业日,
       sh.name AS 班次,
       sh.status AS 班次状态,
       t.status AS 状态,
       t.gross_kg AS 毛重,
       t.tare_kg AS 皮重,
       t.deduct_kg AS 扣杂,
       t.net_kg AS 净重,
       t.grade_id AS 品级编号,
       g.category AS 品类,
       g.grade_name AS 品级,
       t.locked_price AS 锁价,
       t.amount AS 金额,
       t.note AS 备注,
       t.created_at AS 入站时间,
       t.settled_at AS 结价时间,
       t.voided_at AS 销单时间
FROM tickets t
JOIN sites st ON st.id = t.site_id
JOIN scales sc ON sc.id = t.scale_id
JOIN shifts sh ON sh.id = t.shift_id
LEFT JOIN grades g ON g.id = t.grade_id
"""


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def audit(conn, kind: str, ref_id: int | None, action: str, note: str = "") -> None:
    conn.execute(
        "INSERT INTO audit_events(kind, ref_id, action, created_at, note) VALUES (?, ?, ?, ?, ?)",
        (kind, ref_id, action, now_str(), note),
    )


def get_setting(conn, key: str, default: str = "") -> str:
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def current_shift(conn):
    row = conn.execute(
        "SELECT * FROM shifts WHERE status='未落印' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if not row:
        raise HTTPException(400, "无未落印班次")
    return row


def assert_shift_writable(conn, shift_id: int) -> None:
    row = conn.execute("SELECT status FROM shifts WHERE id=?", (shift_id,)).fetchone()
    if not row:
        raise HTTPException(400, "班次不存在")
    if row["status"] != "未落印":
        raise HTTPException(400, "班次已落印，禁止改磅条")


def next_serial(conn) -> str:
    day = datetime.now().strftime("%Y%m%d")
    prefix = f"磅{day}"
    row = conn.execute(
        "SELECT serial FROM tickets WHERE serial LIKE ? ORDER BY serial DESC LIMIT 1",
        (prefix + "%",),
    ).fetchone()
    n = 1
    if row and len(row["serial"]) >= 4:
        try:
            n = int(row["serial"][-4:]) + 1
        except ValueError:
            n = 1
    return f"{prefix}{n:04d}"


def ticket_view(conn, ticket_id: int) -> dict | None:
    row = conn.execute(TICKET_SELECT + " WHERE t.id=?", (ticket_id,)).fetchone()
    return dict(row) if row else None


def require_ticket(conn, ticket_id: int):
    row = conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
    if not row:
        raise HTTPException(404, "磅条不存在")
    return row


def occupy_scale(conn, scale_id: int) -> None:
    cur = conn.execute(
        "UPDATE scales SET status='占用' WHERE id=? AND status='空闲'",
        (scale_id,),
    )
    if cur.rowcount == 1:
        return
    row = conn.execute("SELECT status FROM scales WHERE id=?", (scale_id,)).fetchone()
    if not row:
        raise HTTPException(404, "地磅不存在")
    if row["status"] == "故障":
        raise HTTPException(400, "地磅故障，不能过磅")
    if row["status"] == "占用":
        raise HTTPException(400, "地磅占用中")
    raise HTTPException(400, "地磅不可占用")


def release_scale(conn, scale_id: int) -> None:
    still = conn.execute(
        "SELECT COUNT(*) AS c FROM tickets WHERE scale_id=? AND status IN ('待定级','待结价')",
        (scale_id,),
    ).fetchone()["c"]
    if still == 0:
        conn.execute(
            "UPDATE scales SET status='空闲' WHERE id=? AND status='占用'",
            (scale_id,),
        )
