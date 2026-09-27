from app.models.schemas import AdvisoryAction


def create_advisory(
    crop: str,
    growth_stage: str,
    rainfall: float,
    rain_probability: float,
    temperature: float,
    humidity: float,
    wind_speed: float,
) -> dict:
    heavy_rain = rainfall >= 25 or rain_probability >= 80
    moderate_rain = rainfall >= 15 or rain_probability >= 60
    heat = temperature >= 35
    strong_wind = wind_speed >= 15
    high_humidity = humidity >= 80

    actions: list[AdvisoryAction] = []

    if heavy_rain:
        actions.append(
            AdvisoryAction(
                title="Avoid irrigation",
                description="Expected rainfall may provide enough moisture and increase excess-water risk.",
            )
        )
    elif moderate_rain:
        actions.append(
            AdvisoryAction(
                title="Review irrigation timing",
                description="Check field moisture before the next irrigation cycle.",
            )
        )
    else:
        actions.append(
            AdvisoryAction(
                title="Monitor soil moisture",
                description="Lower rainfall may require irrigation depending on soil moisture and crop demand.",
            )
        )

    if heavy_rain:
        actions.append(
            AdvisoryAction(
                title="Protect field drainage",
                description="Inspect drainage channels and low-lying field sections before rainfall.",
            )
        )
    else:
        actions.append(
            AdvisoryAction(
                title="Field operations can continue",
                description="Conditions are comparatively suitable for routine field activity.",
            )
        )

    if high_humidity:
        actions.append(
            AdvisoryAction(
                title="Monitor for disease",
                description="Humid conditions can increase suitability for some moisture-related crop diseases.",
            )
        )
    else:
        actions.append(
            AdvisoryAction(
                title="Continue crop monitoring",
                description="Regular scouting should continue through the current crop stage.",
            )
        )

    if heat:
        actions.append(
            AdvisoryAction(
                title="Monitor heat stress",
                description="Higher daytime temperatures can increase crop water demand.",
            )
        )
    elif strong_wind:
        actions.append(
            AdvisoryAction(
                title="Check wind-sensitive operations",
                description="Review activities that are sensitive to stronger winds.",
            )
        )
    else:
        actions.append(
            AdvisoryAction(
                title="Normal crop monitoring",
                description="No major temperature or wind concern is indicated by this prototype forecast.",
            )
        )

    if heavy_rain or (heat and high_humidity):
        level = "High"
    elif moderate_rain or heat or strong_wind:
        level = "Medium"
    else:
        level = "Low"

    if level == "High":
        summary = f"Weather conditions require closer attention for {crop} during the {growth_stage.lower()} stage."
    elif level == "Medium":
        summary = f"Some weather-related adjustments may be useful for {crop} during the {growth_stage.lower()} stage."
    else:
        summary = f"Current weather conditions show no major immediate advisory concern for {crop}."

    return {
        "level": level,
        "summary": summary,
        "actions": actions,
        "rainfall_risk": "High" if heavy_rain else "Medium" if moderate_rain else "Low",
        "heat_risk": "Medium" if heat else "Low",
        "wind_risk": "Medium" if strong_wind else "Low",
        "moisture_risk": "Medium" if high_humidity else "Low",
        "irrigation": (
            "Delay irrigation and reassess field moisture after rainfall."
            if heavy_rain
            else "Check soil moisture before irrigation."
            if moderate_rain
            else "Irrigate according to soil moisture and crop requirement."
        ),
        "field_operations": (
            "Avoid unnecessary field operations during rainfall."
            if heavy_rain
            else "Avoid wind-sensitive operations during stronger winds."
            if strong_wind
            else "Routine field operations can continue with normal precautions."
        ),
        "monitoring": (
            "Increase monitoring for moisture-related pest and disease conditions."
            if high_humidity
            else "Continue regular crop and field monitoring."
        ),
    }
