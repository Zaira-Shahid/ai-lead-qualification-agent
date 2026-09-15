from fastapi import FastAPI

from app.api import health

app = FastAPI(title="AI Lead Qualification Agent")

app.include_router(health.router)
