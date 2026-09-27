# GramMausam AI Backend

FastAPI + Python backend for the GramMausam AI prototype. The repository covers the complete development path from API foundation and demo data to geospatial utilities, baseline/ML downscaling, model evaluation, risk alerts, agricultural advisory rules, database configuration and REST API integration.

## Important project note

The included demo dataset is synthetic and exists only so the whole pipeline can be run locally without exposing credentials or depending on external data during development. The trained metrics produced from this demo data must not be presented as real-world model accuracy.

For the final SIH implementation, replace the demo data with properly sourced forecast/observation pairs and validated administrative/geospatial datasets.

## Folder structure

```text
backend/
├── app/
│   ├── api/
│   ├── data/
│   ├── geo/
│   ├── ml/
│   ├── models/
│   ├── services/
│   ├── config.py
│   ├── db.py
│   └── main.py
├── data/
│   ├── raw/
│   └── processed/
├── models/
├── scripts/
├── tests/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Local setup on Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`.

Start the API:

```powershell
uvicorn app.main:app --reload
```

API docs:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

Health check:

```text
GET /api/health
```

## Demo ML pipeline

Generate a synthetic training dataset:

```powershell
python -m scripts.generate_demo_data
```

Train the five demonstration models:

```powershell
python -m scripts.train_models
```

Evaluate the saved models:

```powershell
python -m scripts.evaluate_models
```

The current training pipeline uses RandomForestRegressor for a stable, easy-to-run baseline. The code is intentionally modular so a more appropriate model can be substituted later after the real data characteristics are known.

## Downscaling targets

Supported targets:

- rainfall
- max_temp
- min_temp
- humidity
- wind_speed

The current feature set is:

- coarse forecast variables
- elevation
- NDVI
- soil moisture
- land-cover code
- day of year

These are demonstration features. Final feature selection should be driven by the actual datasets that can be obtained for the target region.

## API examples

Get weather:

```text
GET /api/weather/Bara
```

Get forecast:

```text
GET /api/forecast/Bara?days=7
```

Get Panchayats:

```text
GET /api/panchayats
```

Get a downscaled target:

```text
GET /api/downscaling/Bara/rainfall
GET /api/downscaling/Bara/max_temp
GET /api/downscaling/Bara/humidity
```

Send custom rainfall features:

```http
POST /api/downscaling/predict
Content-Type: application/json

{
  "coarse_rainfall": 20,
  "coarse_max_temp": 32,
  "coarse_min_temp": 24,
  "coarse_humidity": 78,
  "coarse_wind_speed": 12,
  "elevation": 100,
  "ndvi": 0.5,
  "soil_moisture": 0.6,
  "land_cover_code": 12,
  "day_of_year": 114
}
```

Advisory:

```http
POST /api/advisory
Content-Type: application/json

{
  "crop": "Wheat",
  "growth_stage": "Vegetative Stage",
  "rainfall": 18,
  "rain_probability": 72,
  "temperature": 32,
  "humidity": 78,
  "wind_speed": 12
}
```

## Geospatial workflow

The intended production pipeline is:

```text
Coarse Forecast
      +
Historical Observation
      +
Panchayat/Block Boundaries
      +
Terrain / Satellite / Soil Features
            ↓
      Feature Engineering
            ↓
       Fine Grid
            ↓
   Downscaling Model
            ↓
   Grid-cell Predictions
            ↓
  Panchayat Aggregation
            ↓
       Risk Engine
            ↓
   Advisory / API Output
```

The utilities in `app/geo/` provide building blocks for this workflow. They do not claim to replace scientific GIS preprocessing of the final production datasets.

## Database

`DATABASE_URL` is optional in local demo mode. When configured, the project provides SQLAlchemy/PostGIS-ready database configuration in `app/db.py`.

The included `docker-compose.yml` starts a PostGIS database for development. Before using it outside a local environment, change the example database password and move credentials to environment variables.

## Frontend connection

The React application can call the backend through the REST routes above. For local development:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
```

Do not put private backend/database credentials in Vite `VITE_*` variables. Browser-exposed variables are not secrets.

## No external AI credentials

This repository does not use OpenAI, ChatGPT, Gemini or any other LLM API key. Agricultural recommendations are implemented as deterministic backend rules for the prototype. An LLM can be added later only as an optional explanation/translation layer, with scientific advisory rules remaining the source of truth.

## Testing

```powershell
pytest -q
```
