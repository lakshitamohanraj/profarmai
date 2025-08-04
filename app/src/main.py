# from langchain_groq import ChatGroq
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from dotenv import load_dotenv
# import os


# def run(user_prompt:str):
#     # user_prompt = input("Enter your question for the AI: ")
#     load_dotenv()
#     prompt = PromptTemplate(
#         input_variables=["question"],
#         template="Answer the following question in a clear and helpful way:\n\n{question}"
#     )

#     llm = ChatGroq(
#         groq_api_key=os.getenv("GROQ_API_KEY"),
#         model_name="llama3-8b-8192"  # You can switch to "llama3-70b-8192" or others
#     )

#     chain = prompt | llm

#     response = chain.invoke({"question": user_prompt})
#     return response
   
# # print(run("what is a joke?").content)


from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
# from langchain_community.chat_message_histories.sqlite import SQLiteChatMessageHistory

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

# Conversation run function with memory
def run(user_prompt: str, session_id: str):
    memory = get_memory(session_id)

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-8b-8192"
    )
   # parse user query , get param values 
   # hit ml model get score + trend
   # navigate 
    # Set up conversation chain with memory
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

    response = conversation.invoke({"input": user_prompt})
    return response


