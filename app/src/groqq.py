import os
import requests
from dotenv import load_dotenv

load_dotenv()

def list_groq_models():
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
    }
    response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
    if response.status_code == 200:
        models = response.json()
        print("Available models in your Groq account:")
        for model in models.get("data", []):
            print(f"- {model['id']}")
    else:
        print(f"Failed to fetch models. Status code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    list_groq_models()
