from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Step 1: Get user input
user_prompt = input("Enter your question for the AI: ")

# Step 2: Define your prompt template
prompt = PromptTemplate(
    input_variables=["question"],
    template="Answer the following question in a clear and helpful way:\n\n{question}"
)

# Step 3: Initialize the ChatGroq model
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-8b-8192"  # You can switch to "llama3-70b-8192" or others
)

# Step 4: Chain the prompt and the model
chain = LLMChain(prompt=prompt, llm=llm)

# Step 5: Run the chain with the user input
response = chain.run({"question": user_prompt})

# Step 6: Print the result
print("\nAI Response:")
print(response)
