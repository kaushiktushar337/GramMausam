from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Panchayat(Base):
    __tablename__ = "panchayats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    state: Mapped[str] = mapped_column(String(80))
    district: Mapped[str] = mapped_column(String(80))
    block: Mapped[str] = mapped_column(String(80))
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    panchayat: Mapped[str] = mapped_column(String(120), index=True)
    observed_on: Mapped[date] = mapped_column(Date, index=True)
    rainfall: Mapped[float] = mapped_column(Float)
    max_temp: Mapped[float] = mapped_column(Float)
    min_temp: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    wind_speed: Mapped[float] = mapped_column(Float)


class ForecastRecord(Base):
    __tablename__ = "forecast_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    panchayat: Mapped[str] = mapped_column(String(120), index=True)
    forecast_date: Mapped[date] = mapped_column(Date, index=True)
    rainfall: Mapped[float] = mapped_column(Float)
    rain_probability: Mapped[float] = mapped_column(Float)
    max_temp: Mapped[float] = mapped_column(Float)
    min_temp: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    wind_speed: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(80), default="unknown")


class DownscaledPrediction(Base):
    __tablename__ = "downscaled_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    panchayat: Mapped[str] = mapped_column(String(120), index=True)
    prediction_date: Mapped[date] = mapped_column(Date, index=True)
    target: Mapped[str] = mapped_column(String(40), index=True)
    coarse_value: Mapped[float] = mapped_column(Float)
    downscaled_value: Mapped[float] = mapped_column(Float)
    confidence: Mapped[str] = mapped_column(String(20))
    model_source: Mapped[str] = mapped_column(String(80))


class AdvisoryRecord(Base):
    __tablename__ = "advisories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    panchayat: Mapped[str] = mapped_column(String(120), index=True)
    crop: Mapped[str] = mapped_column(String(80))
    growth_stage: Mapped[str] = mapped_column(String(80))
    level: Mapped[str] = mapped_column(String(20))
    summary: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AlertRecord(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    panchayat: Mapped[str] = mapped_column(String(120), index=True)
    priority: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
