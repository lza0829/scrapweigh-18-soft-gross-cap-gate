from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import PROJECT_NAME
from app.routers import (
    audit,
    dashboard,
    grades,
    grading,
    scales,
    settle,
    settings,
    shifts,
    sites,
    tickets,
    voids,
    weigh,
)
from app.seed import seed_if_empty

seed_if_empty()

app = FastAPI(title=PROJECT_NAME)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
for mod in (
    dashboard,
    sites,
    scales,
    grades,
    weigh,
    tickets,
    grading,
    settle,
    voids,
    shifts,
    settings,
    audit,
):
    app.include_router(mod.router, prefix="/api")


@app.get("/api/健康")
def health():
    return {"产品": PROJECT_NAME, "状态": "正常"}
