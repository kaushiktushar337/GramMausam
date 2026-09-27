const API_BASE_URL = import.meta.env.DEV
  ? ""
  : import.meta.env.VITE_API_BASE_URL || "";

async function request(endpoint, options) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

export function getHealth() {
  return request("/api/health");
}

export async function getPanchayats(search = "", limit = 50, offset = 0) {
  const params = new URLSearchParams({
    search,
    limit: String(limit),
    offset: String(offset),
  });
  const data = await request(`/api/panchayats?${params}`);
  return data.panchayats || [];
}

export function getNearbyPanchayatsFromApi(panchayat, limit = 8) {
  const params = new URLSearchParams({ limit: String(limit) });
  return request(
    `/api/panchayats/${encodeURIComponent(panchayat)}/nearby?${params}`
  );
}

export async function getWeatherFromApi(panchayat) {
  const data = await request(
    `/api/weather/${encodeURIComponent(panchayat)}`
  );

  return {
    panchayat: data.panchayat,
    date: data.date,
    rainfall: data.rainfall,
    rainfallRange: data.rainfall_range,
    maxTemp: data.max_temp,
    minTemp: data.min_temp,
    humidity: data.humidity,
    windSpeed: data.wind_speed,
    windDirection: data.wind_direction,
    condition: data.condition,
    confidence: data.confidence,
    confidenceValue: data.confidence_value,
    risk: data.risk,
    riskText: data.risk_text,
  };
}

export async function getForecastFromApi(panchayat) {
  const data = await request(
    `/api/forecast/${encodeURIComponent(panchayat)}`
  );

  return data.map((item) => ({
    date: item.date,
    day: item.day,
    rainfall: item.rainfall,
    rainProbability: item.rain_probability,
    maxTemp: item.max_temp,
    minTemp: item.min_temp,
    humidity: item.humidity,
    windSpeed: item.wind_speed,
    condition: item.condition,
  }));
}
export async function getHistoricalFromApi(panchayat, days = 30) {
  const data = await request(
    `/api/historical/${encodeURIComponent(panchayat)}?days=${days}`
  );

  return data.map((item) => ({
    date: item.date,
    observation: item.observation,
    blockForecast: item.block_forecast,
    downscaled: item.downscaled,
  }));
}

export async function getAdvisoryFromApi({
  crop = "Wheat",
  growthStage = "Vegetative",
  rainfall = 0,
  rainProbability = 0,
  temperature = 0,
  humidity = 0,
  windSpeed = 0,
} = {}) {
  const data = await request("/api/advisory", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        crop,
        growth_stage: growthStage,
        rainfall,
        rain_probability: rainProbability,
        temperature,
        humidity,
        wind_speed: windSpeed,
      }),
    });

  return {
    level: data.level,
    summary: data.summary,
    actions: data.actions,
    rainfallRisk: data.rainfall_risk,
    heatRisk: data.heat_risk,
    windRisk: data.wind_risk,
    moistureRisk: data.moisture_risk,
    irrigation: data.irrigation,
    fieldOperations: data.field_operations,
    monitoring: data.monitoring,
  };
}
export function getAlertsFromApi() {
  return request("/api/alerts");
}