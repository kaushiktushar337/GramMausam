from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

WeatherParameter = Literal[
    "rainfall",
    "max_temp",
    "min_temp",
    "humidity",
    "wind_speed",
]
RiskLevel = Literal["Low", "Medium", "High"]


class WeatherResponse(BaseModel):
    panchayat: str
    date: date
    rainfall: float
    rainfall_range: str
    max_temp: float
    min_temp: float
    humidity: float
    wind_speed: float
    wind_direction: str
    condition: str
    confidence: RiskLevel
    confidence_value: float = Field(ge=0, le=100)
    risk: RiskLevel
    risk_text: str


class ForecastDay(BaseModel):
    date: date
    day: str
    rainfall: float
    rain_probability: float = Field(ge=0, le=100)
    max_temp: float
    min_temp: float
    humidity: float = Field(ge=0, le=100)
    wind_speed: float
    condition: str


class DownscalingInput(BaseModel):
    coarse_rainfall: float = Field(ge=0)
    coarse_max_temp: float
    coarse_min_temp: float
    coarse_humidity: float = Field(ge=0, le=100)
    coarse_wind_speed: float = Field(ge=0)
    elevation: float = Field(ge=0)
    ndvi: float = Field(ge=-1, le=1)
    soil_moisture: float = Field(ge=0, le=1)
    land_cover_code: int = Field(ge=0)
    day_of_year: int = Field(ge=1, le=366)


class DownscalingResponse(BaseModel):
    target: WeatherParameter
    coarse_value: float
    downscaled_value: float
    unit: str
    confidence: RiskLevel
    model_source: str


class AdvisoryRequest(BaseModel):
    crop: str
    growth_stage: str
    rainfall: float = Field(ge=0)
    rain_probability: float = Field(ge=0, le=100)
    temperature: float
    humidity: float = Field(ge=0, le=100)
    wind_speed: float = Field(ge=0)


class AdvisoryAction(BaseModel):
    title: str
    description: str


class AdvisoryResponse(BaseModel):
    level: RiskLevel
    summary: str
    actions: list[AdvisoryAction]
    rainfall_risk: RiskLevel
    heat_risk: RiskLevel
    wind_risk: RiskLevel
    moisture_risk: RiskLevel
    irrigation: str
    field_operations: str
    monitoring: str


class AlertItem(BaseModel):
    id: str
    panchayat: str
    priority: RiskLevel
    category: str
    title: str
    description: str
    action: str
    time: str
    created_at: datetime


class HistoricalPoint(BaseModel):
    date: date
    observation: float
    block_forecast: float
    downscaled: float


class ModelMetrics(BaseModel):
    target: WeatherParameter
    block_mae: float
    downscaled_mae: float
    block_rmse: float
    downscaled_rmse: float
    sample_count: int
    note: str
