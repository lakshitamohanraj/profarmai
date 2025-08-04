from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
import json


from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
# from langchain_community.chat_message_histories.sqlite import SQLiteChatMessageHistory

from dotenv import load_dotenv
import os

load_dotenv()

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

def get_weather_analysis(weather_data_str,agri_status_str):
    # memory = get_memory(session_id)
    
    with open("D:\\accenture-hackathon\\profarmai\\app\\src\\prompts\\weather_monitor_agent.txt", "r") as f:
        prompt_template = f.read()

    prompt = PromptTemplate(
        input_variables=["weather_data","farmer_agriculture_status"],
        template=prompt_template
    )
    
     # Load dummy JSON
    # with open("D:/accenture-hackathon/profarmai/app/src/agents/weather_data.json", "r") as wf:
    #     weather_data = json.load(wf)

    # with open("D:/accenture-hackathon/profarmai/app/src/agents/farmer_agricultural_status.json", "r") as af:
    #     agri_status = json.load(af)

    # # Convert to string
    # weather_data_str = json.dumps(weather_data, indent=2)
    # agri_status_str = json.dumps(agri_status, indent=2)
    

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-8b-8192"
    )
     
    chain = LLMChain(
        llm=llm,
        verbose=True,
        prompt=prompt
    )

    response = chain.invoke({
        "weather_data": weather_data_str,
        "farmer_agriculture_status":agri_status_str
        })
    filename = "D:/accenture-hackathon/profarmai/app/src/agents/weather_analysis_output.json"
    # print(type(response['text']))
    try:
        with open(filename, 'w') as json_file:
            json.dump(json.loads(response['text']), json_file, indent=4) # indent=4 for pretty printing
        print(f"JSON file '{filename}' created successfully.")
    except IOError as e:
        print(f"Error creating file: {e}")
        
    return response



def get_weather_related_risks(weather_data_str,finance_status_str):
        
    with open("D:\\accenture-hackathon\\profarmai\\app\\src\\prompts\\weather_risk_mitigator.txt", "r") as f:
        prompt_template = f.read()

    prompt = PromptTemplate(
        input_variables=["weather_analysis_report","financial_memory_snapshot"],
        template=prompt_template
    )
    
    #  # Load dummy JSON
    # with open("D:/accenture-hackathon/profarmai/app/src/agents/weather_analysis_output.json", "r") as wf:
    #     weather_analysis = json.load(wf)
    # # app\src\agents\financial_memory_summary.json
    # with open("D:/accenture-hackathon/profarmai/app/src/agents/financial_memory_summary.json", "r") as af:
    #     finance_stats = json.load(af)

    # # Convert to string
    # weather_data_str = json.dumps(weather_analysis, indent=2)
    # finance_status_str = json.dumps(finance_stats, indent=2)
    

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-8b-8192"
    )
     
    chain = LLMChain(
        llm=llm,
        # memory=memory,
        verbose=True,
        prompt=prompt
    )

    response = chain.invoke({
        "weather_analysis_report": weather_data_str,
        "financial_memory_snapshot":finance_status_str
        })
    return response

    


