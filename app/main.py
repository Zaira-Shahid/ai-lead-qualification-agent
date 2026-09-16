import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import chat, health, leads, qualify
from app.database.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="AI Lead Qualification Agent")

init_db()

app.include_router(health.router)
app.include_router(leads.router)
app.include_router(chat.router)
app.include_router(qualify.router)

# Serves the static chat UI (frontend/index.html, style.css, app.js) at "/".
# Mounted last so it does not shadow the API routes above.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
