from datetime import date, timedelta

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
    forecast = response.json()
    assert len(forecast) == 3
    assert "max_temp" in forecast[0]
    assert [item["date"] for item in forecast] == [
        (date.today() + timedelta(days=offset)).isoformat()
        for offset in range(3)
    ]


def test_historical_periods_share_consistent_daily_values():
    three_day = client.get("/api/historical/Bara?days=3").json()
    seven_day = client.get("/api/historical/Bara?days=7").json()

    assert len(three_day) == 3
    assert len(seven_day) == 7
    assert three_day == seven_day[-3:]
    assert len({item["observation"] for item in seven_day}) > 1


def test_panchayat_boundary():
    response = client.get("/api/panchayats/ABHAUDOPURA/boundary")
    assert response.status_code == 200
    boundary = response.json()
    assert boundary["type"] == "FeatureCollection"
    assert boundary["features"][0]["properties"]["gpname"] == "ABHAUDOPURA"


def test_nearby_panchayats_include_weather():
    response = client.get("/api/panchayats/ABHAUDOPURA/nearby?limit=5")
    assert response.status_code == 200
    features = response.json()["features"]
    assert len(features) == 5
    assert features[0]["properties"]["gpname"] == "ABHAUDOPURA"
    weather = features[0]["properties"]["weather"]
    assert weather["rainfall"] >= 0
    assert weather["windSpeed"] >= 0
    assert weather["minTemp"] <= weather["maxTemp"]
    assert weather["date"]


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
