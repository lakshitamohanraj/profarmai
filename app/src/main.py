# from utils.weather_api import get_weather_forecast
# from agents.weather_agent import create_weather_chain
# import pandas as pd
# import json

# def run():
#     lat, lon = 28.6139, 77.2090  # Example: New Delhi, India

#     print("Fetching weather data...")
#     weather_data = get_weather_forecast(lat, lon)
#     weather_str = json.dumps(weather_data, indent=2)

#     chain = create_weather_chain()
#     result = chain.run(weather_data=weather_str)

#     print("\n=== Weather-Aware Risk Mitigation Strategy ===\n")
#     print(result)

# def categorize(value, low, high):
#     if value < low:
#         return "low"
#     elif value > high:
#         return "high"
#     else:
#         return "medium"
    
# def preprocess():
#     df = pd.read_csv("D:\\accenture-hackathon\\profarmai\\data\\farmer_advisor_dataset.csv")
    
    
#     df['pesticide_level'] = df['Pesticide_Usage_kg'].apply(lambda x: categorize(x, 5.675684 , 15.330758))
#     df['fertilizer_level'] = df['Fertilizer_Usage_kg'].apply(lambda x: categorize(x, 87.945625 , 162.619398))
#     df['yield_level'] = df['Crop_Yield_ton'].apply(lambda x: categorize(x, 3.218402 ,7.740585))
#      df['soilph_level'] = df['Pesticide_Usage_kg'].apply(lambda x: categorize(x, pesticide_25, pesticide_75))
#     df['temperatureC_level'] = df['Fertilizer_Usage_kg'].apply(lambda x: categorize(x, fert_25, fert_75))
#     df['soilmoisture_level'] = df['Crop_Yield_ton'].apply(lambda x: categorize(x, yield_25, yield_75))
#      df['rainfallmm_level'] = df['Pesticide_Usage_kg'].apply(lambda x: categorize(x, pesticide_25, pesticide_75))
#     df['sustainabilityscore_level'] = df['Fertilizer_Usage_kg'].apply(lambda x: categorize(x, fert_25, fert_75))
    


# if __name__ == "__main__":
#     # run()
#     preprocess()
