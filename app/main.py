from fastapi import FastAPI

from app.api import health, leads
from app.database.database import init_db

app = FastAPI(title="AI Lead Qualification Agent")

init_db()

app.include_router(health.router)
app.include_router(leads.router)
