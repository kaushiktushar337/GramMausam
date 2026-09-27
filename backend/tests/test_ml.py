from app.ml.predict import confidence_from_error


def test_confidence_low_error():
    assert confidence_from_error(20, 20, 0.5) == "High"


def test_confidence_medium_error():
    assert confidence_from_error(20, 20, 2.0) == "Medium"


def test_confidence_high_error():
    assert confidence_from_error(20, 20, 5.0) == "Low"
