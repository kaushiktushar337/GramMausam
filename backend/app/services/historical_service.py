from app.data.demo import make_historical


def get_historical(panchayat: str, days: int = 30) -> list[dict]:
    return make_historical(panchayat, min(days, 365))
