from __future__ import annotations
import os
from pathlib import Path

PROJECT_NAME = "旧物磅条"
ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.environ.get("SCRAPWEIGH_DB", str(ROOT / "data" / "scrapweigh.db")))
