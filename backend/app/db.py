from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from app.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS sites (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT '营业中' CHECK(status IN ('营业中','停收','已注销')),
  address TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS scales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  site_id INTEGER NOT NULL,
  code TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT '空闲' CHECK(status IN ('空闲','占用','故障')),
  note TEXT NOT NULL DEFAULT '',
  UNIQUE(site_id, code),
  FOREIGN KEY(site_id) REFERENCES sites(id)
);
CREATE TABLE IF NOT EXISTS grades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category TEXT NOT NULL,
  grade_name TEXT NOT NULL,
  unit_price REAL NOT NULL,
  UNIQUE(category, grade_name)
);
CREATE TABLE IF NOT EXISTS shifts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_day TEXT NOT NULL,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT '未落印' CHECK(status IN ('未落印','已落印')),
  stamped_at TEXT,
  UNIQUE(business_day, name)
);
CREATE TABLE IF NOT EXISTS tickets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  serial TEXT NOT NULL UNIQUE,
  site_id INTEGER NOT NULL,
  scale_id INTEGER NOT NULL,
  shift_id INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT '待定级' CHECK(status IN ('待定级','待结价','已结价','已销')),
  gross_kg REAL NOT NULL,
  tare_kg REAL NOT NULL,
  deduct_kg REAL NOT NULL DEFAULT 0,
  net_kg REAL NOT NULL,
  grade_id INTEGER,
  locked_price REAL,
  amount REAL,
  note TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  settled_at TEXT,
  voided_at TEXT,
  FOREIGN KEY(site_id) REFERENCES sites(id),
  FOREIGN KEY(scale_id) REFERENCES scales(id),
  FOREIGN KEY(shift_id) REFERENCES shifts(id),
  FOREIGN KEY(grade_id) REFERENCES grades(id)
);
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  ref_id INTEGER,
  action TEXT NOT NULL,
  created_at TEXT NOT NULL,
  note TEXT NOT NULL DEFAULT ''
);
"""

TICKET_STATUSES = ("待定级", "待结价", "已结价", "已销")
SCALE_STATUSES = ("空闲", "占用", "故障")
SITE_STATUSES = ("营业中", "停收", "已注销")
SHIFT_STATUSES = ("未落印", "已落印")


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with db() as conn:
        conn.executescript(SCHEMA)


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None


def rows_to_list(rows) -> list[dict]:
    return [dict(r) for r in rows]
