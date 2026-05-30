from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import (
    patients,
    conflicts,
    reliability,
    audit
)

app = FastAPI(
    title="Maternal Health Conflict Resolution API"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    patients.router
)

app.include_router(
    conflicts.router
)

app.include_router(
    reliability.router
)

app.include_router(
    audit.router
)


@app.get("/")
def home():

    return {
        "message":
        "Maternal Health API Running"
    }