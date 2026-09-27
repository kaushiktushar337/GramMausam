from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, advisory, downscaling, forecast, historical, model, panchayats, weather
from app.config import APP_NAME, CORS_ORIGINS, ENVIRONMENT

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
    allow_origins=CORS_ORIGINS,
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
