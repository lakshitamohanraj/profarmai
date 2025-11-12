# ================================
# fetch_and_store_weather_data.py
# ================================
import requests
import json
import os

def get_location_from_ip():
    """Fetch approximate latitude and longitude based on current public IP."""
    try:
        response = requests.get("https://ipinfo.io/json")
        response.raise_for_status()
        data = response.json()

        if "loc" in data:
            lat, lon = map(float, data["loc"].split(","))
            print(f"📍 Detected location: {data.get('city')}, {data.get('country')} ({lat}, {lon})")
            return lat, lon
        else:
            raise ValueError("No location found in response.")

    except Exception as e:
        print(f"⚠️ Could not fetch location automatically: {e}")
        # fallback to Chennai if IP detection fails
        return 13.0827, 80.2707

def fetch_and_store_weather_data(lat: float, lon: float, api_key: str, save_path: str):
    """Fetch weather data from Weatherbit API and save as JSON file."""
    try:
        url = f"https://api.weatherbit.io/v2.0/current?lat={lat}&lon={lon}&key={api_key}"
        response = requests.get(url)
        response.raise_for_status()  # raises error if API fails

        data = response.json()
        if "data" not in data or len(data["data"]) == 0:
            raise ValueError("No weather data returned from API.")

        # Save the first (current) data point to file
        weather_data = data["data"][0]

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(weather_data, f, indent=2)

        print(f"✅ Weather data saved to: {save_path}")
        return weather_data

    except Exception as e:
        print(f"❌ Failed to fetch or save weather data: {e}")
        return None
