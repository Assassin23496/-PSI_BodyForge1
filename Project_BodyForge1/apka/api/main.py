from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..db import database, metadata
from ..container import create_db_engine, profile_repository
from ..infrastructure.services.scheduler import start_scheduler
from .routers import profiles
from  .auth import router as auth_router


app = FastAPI(title="BodyForge API", version="0.1.0")


# CORS – pozwala później gadać z frontem JS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # Połączenie z bazą
    await database.connect()

    # Tworzenie tabel jeśli jeszcze nie istnieją
    engine = create_db_engine()
    metadata.create_all(engine)

    # Startujemy scheduler co 14 dni oznaczający potrzebę aktualizacji BMI
    start_scheduler(profile_repository)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Rejestrujemy routery
app.include_router(profiles.router)


@app.get("/")
async def root():
    return {"message": "BodyForge API działa. Sprawdź /docs"}

app.include_router(auth_router)
