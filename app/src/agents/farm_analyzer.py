import csv
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Set up LLM (TinyLLaMA or other Ollama model)
llm = Ollama(model="tinyllama")

# Load prompt template
with open("app/src/prompts/farm_analyzer_prompt.txt") as f:
    prompt_template = PromptTemplate.from_template(f.read())

# Build LLM chain
chain = LLMChain(llm=llm, prompt=prompt_template)

# Input and output paths
input_csv = "app/data/farm_data.csv"
output_csv = "app/data/farm_analysis_with_advice.csv"

# Process each row
with open(input_csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = list(reader)

results = []

for row in rows:
    # Format input for prompt
    input_data = {k: row[k] for k in prompt_template.input_variables}
    response = chain.run(input_data)

    # Parse and append to row
    try:
        parsed = eval(response)  # safe if model returns strict JSON
        row.update(parsed)
    except Exception as e:
        row.update({
            "influencing_factors": "Error parsing response",
            "financial_improvements": "N/A",
            "risk_mitigations": "N/A"
        })
    results.append(row)

# Save new CSV with added columns
fieldnames = list(results[0].keys())

with open(output_csv, mode='w', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print("✅ Analysis saved to", output_csv)
