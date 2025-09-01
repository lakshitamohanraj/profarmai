from langchain_groq import ChatGroq
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
        model_name="llama3-8b-8192"
    )
     
    conversation = ConversationChain(
        llm=llm,
        memory=memory, 
        verbose=True,
    )

    response = conversation.run(user_prompt)
    return response

def get_coordinator_memory(session_id:str):
    message_history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:///mydatabase.db" # sqlite///:memory.db
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=message_history,
        return_messages=True
    )
    return memory

def run(user_prompt: str, session_id: str):
    memory = get_coordinator_memory(session_id)

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="gemma2-9b-it",  # or whichever model you want
    )
 
    tools = [weather_analysis_tool,weather_risk_tool]
    
    with open("C:\\Users\\MUTHU\\Documents\\aproj\\profarm-backend\\profarmai\\app\\src\\prompts\\coordinator_prompt.txt", "r") as f:
        prompt_text = f.read()
    
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

    response = agent.run(user_prompt)
    return response

def get_weather_and_agri_status(user_id:str):
    with open("C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/weather_data.json", "r") as wf:
        weather_data = json.load(wf)

    with open("C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/farmer_agricultural_status.json", "r") as af:
        agri_status = json.load(af)

    # Convert to string
    weather_data_str = json.dumps(weather_data, indent=2)
    agri_status_str = json.dumps(agri_status, indent=2)
    return weather_data_str,agri_status_str

def get_weather_and_finance_status(user_id:str):
    filepath="C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/weather_analysis_output.json"
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(f"File '{filepath}' is empty or does not exist. Writing empty string.")
        with open(filepath, 'w') as f:
            f.write("")
        weather_analysis="Empty at the moment.."  # Return an empty string as per the requirement
    else:
        with open("C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/weather_analysis_output.json", "r") as wf:
            weather_analysis = json.load(wf)
    # app\src\agents\financial_memory_summary.json
    with open("C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/financial_memory_summary.json", "r") as af:
        finance_stats = json.load(af)

    # Convert to string
    weather_data_str = json.dumps(weather_analysis, indent=2)
    finance_status_str = json.dumps(finance_stats, indent=2)
    return weather_data_str,finance_status_str
    


@tool
def weather_analysis_tool(user_id:str) -> str:
    """Get weather forecast analysis for the farmer's agriculture"""
    weather_data, agri_status = get_weather_and_agri_status(user_id)
    return get_weather_analysis(weather_data, agri_status)

@tool
def weather_risk_tool(user_id:str) -> str:
    """Get weather risk forecast for the farmer's region and agriculture."""
    weather_data, finance_status = get_weather_and_finance_status(user_id)
    return get_weather_analysis(weather_data, finance_status)

@tool
def market_recommendation_tool() -> str:
    """Get Buyer and Seller Market based analysis and possible opportunities shiftings or new partnerships"""
    return get_market_analysis()['text']

