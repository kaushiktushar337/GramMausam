from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_weather():
    response = client.get("/api/weather/Bara")
    assert response.status_code == 200
    data = response.json()
    assert data["panchayat"] == "Bara"
    assert "rainfall" in data


def test_forecast():
    response = client.get("/api/forecast/Bara?days=3")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert "max_temp" in response.json()[0]


def test_downscaling():
    response = client.get("/api/downscaling/Bara/rainfall")
    assert response.status_code == 200
    data = response.json()
    assert data["target"] == "rainfall"
    assert data["unit"] == "mm"


def test_advisory():
    payload = {
        "crop": "Wheat",
        "growth_stage": "Vegetative Stage",
        "rainfall": 28,
        "rain_probability": 82,
        "temperature": 32,
        "humidity": 81,
        "wind_speed": 12,
    }
    response = client.post("/api/advisory", json=payload)
    assert response.status_code == 200
    assert response.json()["level"] in {"Low", "Medium", "High"}


def test_alerts():
    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(alert["category"] == "Heavy Rainfall" for alert in data)
    assert all(alert["time"].startswith("Prediction date: ") for alert in data)
