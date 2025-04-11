from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama

def create_weather_chain():
    llm = Ollama(model="tinyllama", temperature=0.7)

    with open("D:\\accenture-hackathon\\profarmai\\app\\src\\prompts\\weather_prompt.txt", "r") as f:
        prompt_template = f.read()

    prompt = PromptTemplate(
        input_variables=["weather_data"],
        template=prompt_template
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    print(chain.invoke("""Given a farm with the following data:
- Fertilizer_Usage_kg = 131.69
- Pesticide_Usage_kg = 2.96
- Crop_Yield_ton = 1.58
- Sustainability_Score = 51.91
- Sustainability_Efficiency = 0.0117 (Crop_Yield_ton / (Fertilizer_Usage_kg + Pesticide_Usage_kg))
- Cost_Spent = 300.0 (assume $2/kg fertilizer, $5/kg pesticide)
- Env_Risk_Level = Medium
Provide:
1. A financial-sustainability advice statement (1-2 sentences).
2. A risk mitigation tip (1 sentence)."""))
    return chain
