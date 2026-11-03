from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import audit, auth, conflicts, patients, reliability, reviews

app = FastAPI(title="Maternal Health Conflict Resolution API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(conflicts.router)
app.include_router(reliability.router)
app.include_router(audit.router)
app.include_router(reviews.router)


@app.get("/")
def home():
    return {"message": "Maternal Health API Running"}
