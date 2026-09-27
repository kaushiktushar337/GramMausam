from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, advisory, downscaling, forecast, historical, model, panchayats, weather
from app.config import APP_NAME, ENVIRONMENT

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description=(
        "Backend for Panchayat-level weather intelligence, downscaling, "
        "risk alerts and agricultural advisory services."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gram-mausam.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather.router)
app.include_router(forecast.router)
app.include_router(panchayats.router)
app.include_router(downscaling.router)
app.include_router(advisory.router)
app.include_router(alerts.router)
app.include_router(historical.router)
app.include_router(model.router)


@app.get("/api/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "environment": ENVIRONMENT,
        "service": APP_NAME,
    }
