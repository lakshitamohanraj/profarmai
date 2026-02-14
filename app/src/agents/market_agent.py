from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
import json


from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory

import sqlite3
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

def create_weather_chain():
    llm = Ollama(model="tinyllama", temperature=0.7)

    with open("C:\\Users\\MUTHU\\Documents\\aproj\\profarm-backend\\profarmai\\app\\src\\prompts\\weather_prompt.txt", "r") as f:
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



# Setup SQLite message history (persisted memory)
def get_memory(session_id: str):
    message_history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:///mydatabase.db" # sqlite///:memory.db
    )
    memory = ConversationBufferMemory(
        memory_key="history",
        chat_memory=message_history,
        return_messages=True
    )
    return memory

# Conversation run function with memory

def get_market_analysis():
    with open("C:\\Users\\MUTHU\\Documents\\aproj\\profarm-backend\\profarmai\\app\\src\\prompts\\market_research_agent.txt", "r") as f:
        prompt_template = f.read()

    prompt = PromptTemplate(
        input_variables=["current_buyer_data","current_seller_data","current_farmer_market_relation_data","farmer_finance"],
        template=prompt_template
    )
    
     # Load dummy JSON app\src\agents\buyer_market_data.json
    with open("C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/buyer_market_data.json", "r") as wf:
        buyer_data = json.load(wf)

    with open("C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/seller_market_data.json", "r") as af:
        seller_data = json.load(af)
    with open("C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/farmer_market_relation.json", "r") as ff:
        farmer_market_data = json.load(ff)
        
    with open("C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/farmer_profile.json", "r") as kf:
        farmer_profile = json.load(kf)
        
            

    # Convert to string
    buyer_data_str = json.dumps(buyer_data, indent=2)
    farm_market_status_str = json.dumps(seller_data, indent=2)
    seller_data_str = json.dumps(farmer_market_data, indent=2)
    farmer_profile = json.dumps(farmer_profile, indent=2)
    

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="meta-llama/llama-4-scout-17b-16e-instruct"
    )
     
    chain = LLMChain(
        llm=llm,
        # memory=memory,
        verbose=True,
        prompt=prompt
    )

    response = chain.invoke({
        "current_buyer_data": buyer_data_str,
        "current_seller_data":seller_data_str,
        "current_farmer_market_relation_data":farm_market_status_str,
        "farmer_profile":farmer_profile
        })
    
    return response



def get_market_related_risks():
    
    get_market_analysis()
    
    with open("C:\\Users\\MUTHU\\Documents\\aproj\\profarm-backend\\profarmai\\app\\src\\prompts\\weather_risk_mitigator.txt", "r") as f:
        prompt_template = f.read()

    prompt = PromptTemplate(
        input_variables=["weather_analysis_report","financial_memory_snapshot"],
        template=prompt_template
    )
    
     # Load dummy JSON
    with open("C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/weather_analysis_output.json", "r") as wf:
        weather_analysis = json.load(wf)
    # app\src\agents\financial_memory_summary.json
    with open("C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/financial_memory_summary.json", "r") as af:
        finance_stats = json.load(af)

    # Convert to string
    weather_data_str = json.dumps(weather_analysis, indent=2)
    agri_status_str = json.dumps(finance_stats, indent=2)
    

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="gemma2-9b-it",  # or whichever model you want
    )
     
    chain = LLMChain(
        llm=llm,
        # memory=memory,
        verbose=True,
        prompt=prompt
    )

    response = chain.invoke({
        "weather_analysis_report": weather_data_str,
        "financial_memory_snapshot":agri_status_str
        })
    return response

    


# For 2nd version UI

def get_market_context(session_id: str):
    """Fetch only relevant market-related tables and convert to structured JSON context."""
    conn = sqlite3.connect("./app/src/mydatabase.db")
    cursor = conn.cursor()
    market_data = {}
    
    tables = ["market_sellers", "market_buyers", "equipment_records"]

    print("\n=== Fetching Market Context for User:", session_id, "===")
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table} WHERE user_id=?", (session_id,))
            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            formatted_rows = [dict(zip(col_names, row)) for row in rows]
            market_data[table] = formatted_rows
            print(f"✅ Table: {table} -> {len(formatted_rows)} records")
        except Exception as e:
            print(f"⚠️ Error reading table {table}: {e}")

    conn.close()

    # Convert full user context to readable string
    context_str = json.dumps(market_data, indent=2)
    return context_str


def run_market_analyzer(session_id: str, focus: str = "general"):
    """
    Analyze current market situation and generate insights/tips.
    focus can be 'general', 'sellers', 'buyers', or 'equipment' — optional.
    """

    context_str = get_market_context(session_id)

    llm = ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-4o-mini",
        temperature=0.5
    )

    # System prompt guiding the LLM behavior
    system_prompt = """
    You are an expert Agricultural Market Analyst AI that helps Indian farmers understand current market conditions.

    You have access to the farmer's local market data — sellers, buyers, equipment records.
    Your job is to:
    - Identify trends or demand-supply mismatches
    - Recommend where to sell or buy
    - Provide practical market tips and insights
    - Suggest profitable opportunities based on current and external data

    Use plain, farmer-friendly language.
    """

    user_prompt = f"""
    Here is the farmer's recent market context:

    {context_str}

    Analyze this data and provide a tip(short and crisp suggestion) on:
    - Current market trend summary
    - Which items are in high demand
    - Which inputs or equipment might be needed soon
    - Any good opportunities (from external market opportunities) relevant to the farmer
    - Actionable next steps

    Focus area: {focus}
    """

    print("🧩 Running Market Analyzer Agent...")
    response = llm.invoke([SystemMessage(content=system_prompt), SystemMessage(content=user_prompt)])
    return response.content

    