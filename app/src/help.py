import pandas as pd
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()


df = pd.read_csv("D:\\accenture-hackathon\\profarmai\\data\\farmer_advisor_dataset.csv")


def categorize(value, low, high):
    if value < low:
        return "low"
    elif value > high:
        return "high"
    else:
        return "medium"

pesticide_25, pesticide_75 = df['Pesticide_Usage_kg'].quantile([0.25, 0.75])
fert_25, fert_75 = df['Fertilizer_Usage_kg'].quantile([0.25, 0.75])
yield_25, yield_75 = df['Crop_Yield_ton'].quantile([0.25, 0.75])
temp_25, temp_75 = df['Temperature_C'].quantile([0.25, 0.75])
rain_25, rain_75 = df['Rainfall_mm'].quantile([0.25, 0.75])
sust_25, sust_75 = df['Sustainability_Score'].quantile([0.25, 0.75])

df['pesticide_level'] = df['Pesticide_Usage_kg'].apply(lambda x: categorize(x, pesticide_25, pesticide_75))
df['fertilizer_level'] = df['Fertilizer_Usage_kg'].apply(lambda x: categorize(x, fert_25, fert_75))
df['yield_level'] = df['Crop_Yield_ton'].apply(lambda x: categorize(x, yield_25, yield_75))
df['temp_level'] = df['Temperature_C'].apply(lambda x: categorize(x, temp_25, temp_75))
df['rain_level'] = df['Rainfall_mm'].apply(lambda x: categorize(x, rain_25, rain_75))
df['sustainability_level'] = df['Sustainability_Score'].apply(lambda x: categorize(x, sust_25, sust_75))

def influencing_factors(row):
    factors = []
    if row['pesticide_level'] == 'high':
        factors.append("high pesticide")
    if row['fertilizer_level'] == 'high':
        factors.append("high fertilizer")
    if row['yield_level'] == 'low':
        factors.append("low crop yield")
    elif row['yield_level'] == 'high':
        factors.append("high crop yield")
    if row['rain_level'] == 'low':
        factors.append("low rainfall")
    if row['temp_level'] == 'high':
        factors.append("high temperature")
    if row['sustainability_level'] == 'low':
        factors.append("low sustainability")
    return ", ".join(factors)

df['influencing_factors'] = df.apply(influencing_factors, axis=1)

llm = ChatGroq(
    temperature=0.4,
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

template = """
You are a sustainable farming advisor. Based on the following data, give a single-line insight on the farm practice.

Data:
- Crop Type: {crop_type}
- Influencing Factors: {factors}
- Soil pH: {soil_ph}
- Temperature: {temp}
- Rainfall: {rain}
- Fertilizer: {fert}
- Pesticide: {pest}
- Yield: {yield}
- Sustainability Score: {sust_score}

Be specific and actionable. Promote practices that lower the carbon footprint, minimize water consumption, and reduce soil erosion.
"""

prompt = PromptTemplate(
    input_variables=["crop_type", "factors", "soil_ph", "temp", "rain", "fert", "pest", "yield", "sust_score"],
    template=template.strip(),
)

chain = prompt | llm

def generate_insight(row):
    result = chain.invoke({
        "crop_type": row["Crop_Type"],
        "factors": row["influencing_factors"],
        "soil_ph": row["Soil_pH"],
        "temp": row["Temperature_C"],
        "rain": row["Rainfall_mm"],
        "fert": row["Fertilizer_Usage_kg"],
        "pest": row["Pesticide_Usage_kg"],
        "yield": row["Crop_Yield_ton"],
        "sust_score": row["Sustainability_Score"]
    })
    return result.content.strip() if hasattr(result, 'content') else str(result).strip()


# df['insights'] = df.apply(generate_insight, axis=1)

# df[['influencing_factors', 'insights']].to_csv("farm_data_with_factors_and_insights.csv", index=False)
# print("✅ New CSV saved as 'farm_data_with_factors_and_insights.csv'")
