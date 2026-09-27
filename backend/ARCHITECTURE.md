# Backend Architecture

## Runtime flow

```text
React frontend
      |
      | REST / JSON
      v
FastAPI routers
      |
      v
Service layer
      |
      +-------------------+
      |                   |
      v                   v
Weather / Forecast     Advisory / Alerts
      |
      v
Downscaling service
      |
      +-----------------------+
      |                       |
      v                       v
ML model                 Geospatial features
      |                       |
      +-----------+-----------+
                  |
                  v
        PostgreSQL / PostGIS
```

## Downscaling flow

```text
Coarse forecast
      +
Local observations
      +
Terrain / land cover / soil / satellite features
      +
Time features
      |
      v
Feature engineering
      |
      v
Baseline model
      |
      v
ML downscaling model
      |
      v
Fine-grid predictions
      |
      v
Panchayat aggregation
      |
      v
Risk + advisory services
```

## Current prototype boundary

The repository is runnable end-to-end using a deterministic synthetic dataset. This proves the software pipeline, but not real-world weather forecast performance.

Production work begins by replacing the demo generator with approved real forecast/observation data and validating the model spatially and temporally.
