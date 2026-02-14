#from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
import json
from langchain_core.messages import SystemMessage
from langchain_community.chat_message_histories import SQLChatMessageHistory
# from langchain_community.chat_message_histories.sqlite import SQLiteChatMessageHistory
from agents.weather_agent import get_weather_analysis,get_weather_related_risks
from agents.market_agent import get_market_analysis
from agents.rag_pipeline import local_rag_tool  # <--- import the RAG tool
import sqlite3




from dotenv import load_dotenv
import os

load_dotenv()
    
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


def sample_conv(user_prompt: str, session_id: str):
    memory = get_memory(session_id)

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="playai-tts"
    )
     
    conversation = ConversationChain(
        llm=llm,
        memory=memory, 
        verbose=True,
    )

    response = conversation.run(user_prompt)
    return response


def get_coordinator_memory(session_id: str):
    message_history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:///mydatabase.db"
    )

    #Fetch personalized context from your other tables
    conn = sqlite3.connect("./app/src/mydatabase.db")
    cursor = conn.cursor()
    user_data = {}

    tables = ["finance_records", "crop_records", "livestock_records", "equipment_records", "market_sellers","market_buyers","farmer_profiles"]

    print("\n=== Fetching Context for User:", session_id, "===")
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table} WHERE user_id=?", (session_id,))
            rows = cursor.fetchall()

            # Get column names so you can see proper keys instead of tuple indexes
            col_names = [desc[0] for desc in cursor.description]

            formatted_rows = [dict(zip(col_names, row)) for row in rows]
            user_data[table] = formatted_rows

            print(f"\n📘 Table: {table}")
            if formatted_rows:
                for row in formatted_rows:
                    print(row)
            else:
                print("⚠️ No records found for this user.")
        except Exception as e:
            print(f" Error reading table {table}: {e}")


    conn.close()

    #  Create a single long context string
    context_str = json.dumps(user_data, indent=2)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=message_history,
        return_messages=True,
        additional_kwargs={"user_context": context_str}  # 👈 custom context
    )
    return memory, context_str


def run(user_prompt: str, session_id: str):
    #memory = get_coordinator_memory(session_id)
    memory, context_str = get_coordinator_memory(session_id)

    '''llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="meta-llama/llama-4-maverick-17b-128e-instruct",  # or whichever model you want
    )'''
    llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model_name="gpt-4o-mini",  # or "gpt-4o" / "gpt-4.1"
    temperature=0.7
)

 
    tools = [weather_analysis_tool,weather_risk_tool,local_rag_tool ,weather_query_tool]
   
    with open("./app/src/prompts/coordinator_prompt.txt", "r") as f:
        prompt_text = f.read()
    
    #weather_analysis_tool("default_user")  # or actual user_id
    prompt_text += f"\n\nHere is the user's current farm context (for reference):\n{context_str}\n"


    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={
            "system_message": SystemMessage(content=prompt_text)
        }
    )

    # Decide when to call RAG
   
    response = agent.run(user_prompt)
    contextual_prompt = f"""
    Here is background information about the user (for reference only, do not repeat verbatim):

    {context_str}

    Now, respond to the following user query based on that data:
    {user_prompt}
    """
    response = agent.run(contextual_prompt)

    return response

def get_weather_and_agri_status(user_id:str):
    
    with open("./app/src/agents/weather_data.json", "r") as wf:
        weather_data = json.load(wf)

    with open("./app/src/agents/farmer_agricultural_status.json", "r") as af:
        agri_status = json.load(af)

    # Convert to string
    weather_data_str = json.dumps(weather_data, indent=2)
    agri_status_str = json.dumps(agri_status, indent=2)
    return weather_data_str,agri_status_str

def get_weather_and_finance_status(user_id:str):
    filepath="./app/src/agents/weather_analysis_output.json"
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(f"File '{filepath}' is empty or does not exist. Writing empty string.")
        with open(filepath, 'w') as f:
            f.write("")
        weather_analysis="Empty at the moment.."  # Return an empty string as per the requirement
    else:
        with open("./app/src/agents/weather_analysis_output.json", "r") as wf:
            weather_analysis = json.load(wf)
    # app\src\agents\financial_memory_summary.json
    with open("./app/src/agents/financial_memory_summary.json", "r") as af:
        finance_stats = json.load(af)

    # Convert to string
    weather_data_str = json.dumps(weather_analysis, indent=2)
    finance_status_str = json.dumps(finance_stats, indent=2)
    return weather_data_str,finance_status_str
    


@tool
def weather_analysis_tool(user_id:str) -> str:
    """Get weather forecast analysis for the farmer's agriculture"""
    print(">>> Running weather_analysis_tool for user:", user_id)  # Debug
    weather_data, agri_status = get_weather_and_agri_status(user_id)
    result = get_weather_analysis(weather_data, agri_status)
    print(">>> Finished weather_analysis_tool execution.")
    return result

@tool
def weather_risk_tool(user_id:str) -> str:
    """Get weather risk forecast for the farmer's region and agriculture."""
    weather_data, finance_status = get_weather_and_finance_status(user_id)
    return get_weather_related_risks(weather_data, finance_status)

@tool
def market_recommendation_tool() -> str:
    """Get Buyer and Seller Market based analysis and possible opportunities shiftings or new partnerships"""
    return get_market_analysis()['text']

import re

@tool
def weather_query_tool(user_query: str) -> str:
    """Answer weather-related user queries and temperature , humidity queries using the stored weather analysis JSON."""
    try:
        filepath = "./app/src/agents/weather_analysis_output.json"
        with open(filepath, 'r') as f:
            data = json.load(f)

        if "Most Important" in data:
            analysis = data
        else:
            text = data.get("analysis_text", "")
            try:
                analysis = json.loads(text)
            except Exception:
                inner_json = re.search(r"\{[\s\S]*\}", text)
                if not inner_json:
                    return "Sorry, I couldn't find any structured weather analysis data."
                analysis = json.loads(inner_json.group())

        q = user_query.lower()
        if "temperature" in q:
            d = analysis.get("Most Important", {})
            return f"Temperature: {d.get('temperature')}°C — {d.get('reason')}"
        elif "humidity" in q:
            d = analysis.get("Moderately Important", {})
            return f"Humidity: {d.get('humidity')}% — {d.get('reason')}"
        elif "wind" in q or "speed" in q:
            d = analysis.get("Least Important", {})
            return f"Wind speed: {d.get('wind_speed')} km/h — {d.get('reason')}"
        else:
            # If unsure, let the LLM interpret
            from langchain_groq import ChatGroq
            '''llm = ChatGroq(
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model_name="meta-llama/llama-4-maverick-17b-128e-instruct",
            )'''
            llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4o-mini",  # or "gpt-4o" / "gpt-4.1"
            temperature=0.7)

            context = json.dumps(analysis, indent=2)
            prompt = f"""
            Here is the latest weather analysis for the farm:

            {context}

            User question: {user_query}

            Based on the above analysis, provide a concise answer.
            """
            return llm.invoke(prompt).text

    except Exception as e:
        return f"Error reading weather analysis: {e}"
