from utils.weather_api import get_weather_forecast
from agents.weather_agent import create_weather_chain
import json

def run():
    lat, lon = 28.6139, 77.2090  # Example: New Delhi, India

    print("Fetching weather data...")
    weather_data = get_weather_forecast(lat, lon)
    weather_str = json.dumps(weather_data, indent=2)

    chain = create_weather_chain()
    result = chain.run(weather_data=weather_str)

    print("\n=== Weather-Aware Risk Mitigation Strategy ===\n")
    print(result)

if __name__ == "__main__":
    run()
