# GramMausam AI 🌦️🌱

### Panchayat-Level Weather Downscaling for Agro-Meteorological Advisory

GramMausam AI is an applied weather-intelligence prototype that explores how coarse-resolution weather information can be transformed into more localized **Panchayat-level rainfall estimates** and presented through a practical decision-support dashboard.

The system combines data preparation, machine-learning downscaling, geospatial aggregation, risk interpretation, agricultural advisory logic, and a web interface.

> **Current implementation:** The real-data downscaling pipeline currently produces Panchayat-level rainfall predictions. Some additional weather fields shown in the interface are application-layer/demo values and should not be interpreted as independently validated Panchayat-level model outputs.

---

## 🎯 Problem

Weather forecasts are often available at a spatial resolution that may be too coarse for local agricultural decision-making.

A coarse or block-level forecast can hide differences between nearby Panchayats because rainfall and other environmental conditions can vary across relatively small areas.

GramMausam explores a pipeline that:

```text
Coarse Weather Information
          ↓
Fine-Resolution Features
          ↓
ML-Based Downscaling
          ↓
Fine Weather Grid
          ↓
Panchayat Aggregation
          ↓
Risk Interpretation
          ↓
Agricultural Decision Support
```

---

## 💡 Solution

GramMausam uses a hybrid weather-downscaling workflow:

1. Prepare coarse weather information.
2. Construct a finer spatial grid.
3. Combine the coarse rainfall signal with spatial/model features.
4. Predict rainfall at fine-grid locations.
5. Aggregate fine-grid predictions to Panchayat polygons using area-weighted spatial aggregation.
6. Expose the final Panchayat rainfall output through FastAPI.
7. Visualize the information through a React dashboard.
8. Generate simple weather-risk and crop-advisory information.

The core idea is **spatial downscaling**, rather than simply displaying the same coarse forecast for every Panchayat.

---

## 🧠 Current Technical Pipeline

```text
                    Coarse Forecast
                           │
                           ▼
                 Feature Preparation
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
       Rainfall Signal            Spatial Features
             │                           │
             └─────────────┬─────────────┘
                           ▼
                   ML Downscaling
                           │
                           ▼
                    Fine Grid
                       0.05°
                           │
                           ▼
               Panchayat Polygon Join
                           │
                           ▼
                Area-Weighted Mean
                           │
                           ▼
             Panchayat Rainfall Output
                           │
                           ▼
                     FastAPI
                           │
                           ▼
                  React Dashboard
```

---

## 📊 Current Real-Data Example

Example Panchayat: **ABHAUDOPURA**

| Date | Downscaled rainfall |
|---|---:|
| 27 Jul 2025 | 9.92 mm |
| 28 Jul 2025 | 10.27 mm |
| 29 Jul 2025 | 13.19 mm |
| 30 Jul 2025 | 16.88 mm |
| 31 Jul 2025 | 16.42 mm |

These values are from the processed Panchayat-level rainfall output used by the demonstration backend.

---

## ✨ Features

### Weather Intelligence
- Panchayat-level rainfall estimates
- Forecast visualization
- Weather trend presentation
- Panchayat selection
- Localized weather map interface

### Decision Support
- Rainfall risk classification
- Heavy-rainfall alerts
- Crop selection
- Growth-stage selection
- Irrigation guidance
- Field-operation guidance
- Crop monitoring suggestions

### Technical
- Fine-grid rainfall downscaling
- Panchayat polygon aggregation
- REST APIs with FastAPI
- Responsive React interface
- Frontend and backend deployment supported

---

## 🏗️ System Architecture

```text
             External / Open Weather Data
                         │
                         ▼
                  Data Preparation
                         │
                         ▼
                Coarse + Fine Features
                         │
                         ▼
                 ML Downscaling
                         │
                         ▼
                 Fine Grid Output
                         │
                         ▼
             Panchayat Spatial Aggregation
                         │
                         ▼
              Processed Rainfall Dataset
                         │
                         ▼
                   FastAPI Backend
                         │
                         ▼
                  React Frontend
```

---

## 🛠️ Technology Stack

### Frontend

- React.js
- Vite
- JavaScript
- Tailwind CSS
- React Router
- Framer Motion
- Recharts
- React Leaflet
- Leaflet
- Lucide React

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- Pandas
- NumPy
- GeoPandas
- Shapely
- Scikit-learn
- Joblib

### Data and Geospatial Processing

- CHIRPS rainfall data
- GFS-derived forecast data used in the development pipeline
- Fine-resolution grid processing
- Panchayat polygon processing
- Equal-area spatial intersection
- Area-weighted Panchayat aggregation

### Deployment

- **Frontend:** Vercel
- **Backend:** Render
- **Source control:** GitHub

---

## 📁 Repository Structure

```text
GramMausam/
│
├── README.md
├── LICENSE
├── DATA_SOURCES.md
├── .gitignore
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
└── backend/
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
    │
    ├── scripts/
    ├── tests/
    ├── data/
    │   └── processed/
    │       └── panchayat_polygon_rainfall_july2025_test.csv
    │
    ├── models/
    ├── .env.example
    ├── .gitignore
    ├── Dockerfile
    ├── docker-compose.yml
    ├── pyproject.toml
    ├── requirements.txt
    └── requirements-dev.txt
```

---

## 🔌 API

### Health

```http
GET /api/health
```

### Panchayats

```http
GET /api/panchayats
```

### Weather

```http
GET /api/weather/{panchayat}
```

### Forecast

```http
GET /api/forecast/{panchayat}?days=5
```

Example:

```text
/api/forecast/ABHAUDOPURA
```

### Advisory

```http
POST /api/advisory
```

Example:

```json
{
  "crop": "Wheat",
  "growth_stage": "Vegetative",
  "rainfall": 10.27,
  "rain_probability": 70,
  "temperature": 34,
  "humidity": 74,
  "wind_speed": 11
}
```

### Alerts

```http
GET /api/alerts
```

### Historical

```http
GET /api/historical/{panchayat}
```

---

## 💻 Local Development

### Prerequisites

- Node.js and npm
- Python 3.12+
- Git

### Clone

```bash
git clone https://github.com/vibhorsahu26/GramMausam.git
cd GramMausam
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Local frontend:

```text
http://localhost:5173
```

### Backend

```bash
cd backend
python -m venv .venv
```

Windows:

```powershell
.venv\Scriptsctivate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🌐 Deployment

### Frontend

The frontend is deployed on Vercel from:

```text
frontend/
```

Build:

```text
npm run build
```

Output:

```text
dist
```

The production frontend uses the backend base URL through the environment variable:

```text
VITE_API_BASE_URL=<your-backend-url>
```

### Backend

The backend is deployed on Render from:

```text
backend/
```

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🔐 Data and Licensing

GramMausam uses external datasets and geospatial information during development and modelling.

The repository's software licence applies to original project code. It does **not** automatically relicense third-party weather datasets, government datasets, maps, imagery, or other external material.

Some source datasets permit reuse under their own terms, while others may require attribution or have dataset-specific conditions. See [`DATA_SOURCES.md`](DATA_SOURCES.md) before redistributing source or derived data.

The repository intentionally excludes raw and intermediate GIS artifacts, boundary files, model artifacts, credentials, and local environments.

The final processed Panchayat rainfall CSV included in this repository is a derived project output. Its redistribution should be considered together with the terms of the source datasets used to create it.

---

## ⚠️ Current Limitations

GramMausam is a prototype/research-oriented implementation, not an operational national forecasting service.

Current limitations include:

- The real-data ML pipeline currently focuses on rainfall.
- The current real-data demonstration covers a limited test period.
- Some non-rainfall interface values are application-layer/demo values.
- Rainfall probability is currently derived from predicted rainfall for interface compatibility rather than from a separately validated probability model.
- Risk thresholds are application rules and are not official IMD warning thresholds.
- Broader spatial and temporal validation is required before making national-scale accuracy claims.
- Model uncertainty and data-source uncertainty require further evaluation.

---

## 🧪 Model Evaluation

The development workflow includes comparison with a baseline downscaling approach.

Only metrics generated from documented validation experiments should be used as model-performance claims.

The project intentionally avoids unsupported accuracy percentages or improvement claims.

---

## 🤝 Contributing

Create a feature branch:

```bash
git checkout -b feature/your-feature
```

Make changes, test them, then:

```bash
git add .
git commit -m "Describe your change"
git push origin feature/your-feature
```

For substantial changes, document what changed and how it was tested.

---

## 👥 Project

GramMausam was developed as a student project for an applied weather-downscaling and agro-meteorological decision-support use case.

---

## 📄 License

The original project software is licensed under the MIT License in [`LICENSE`](LICENSE).

Third-party datasets, government data, maps, imagery, libraries, and external assets remain subject to their respective terms and licences.

---

## ⭐ Project Flow

```text
Weather Data
     ↓
Data Preparation
     ↓
ML Downscaling
     ↓
Fine Spatial Grid
     ↓
Panchayat Aggregation
     ↓
Risk Analysis
     ↓
Agricultural Advisory
     ↓
FastAPI
     ↓
React Dashboard
```
