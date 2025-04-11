import requests

def get_weather_forecast(lat: float, lon: float):
    # Using Open-Meteo API (no API key needed)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
