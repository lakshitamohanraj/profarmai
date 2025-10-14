# =========================================
# 📚 LOCAL RAG PIPELINE (Text + Ollama + Chroma)
# =========================================
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.tools import tool
import os

# ===============================
# CONFIG
# ===============================
CHROMA_DB_PATH = "C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/local_chroma_db"

# Your farmer success story text
FARMER_TEXT = """
Mr. Veer Shetty Biradar (44) is from Gangapur village, Jharasangam
mandal, in Sangareddy district of Telangana State, India. He is a
graduate and owns 13 acres of dryland and 5 acres of irrigated land.
He grows sugarcane, chickpea, red gram, jowar, bajra, foxtail millet
and finger millet.
Once, while travelling to Maharashtra, Mr. Biradar could not get
any food to eat and suffered from starvation as a result. He started
thinking of producing food for the future generations after coming
back from Maharashtra.
He started growing millets and entered the field of value-added millet
products under the technical guidance of Dr. C.L. Gowda, Deputy
Director General, ICRISAT, and Dr. C.H. Ravindra Reddy, Director,
MSSRF (M.S. Swaminathan Research Foundation), Jeypore, Odisha.
One of the reasons for focusing on value added millet products is
the emergence of lifestyle diseases among the urban population and
prevalence of junk food consumption among the youth. Keeping
all these factors in mind, in 2009, Mr. Biradar started a valueadded
centre for millets in Huda Colony, Chandanagar, Hyderabad,
Telangana, India, in the name of SS Bhavani Foods Pvt. Ltd. Within a
span of seven years, his company developed 60 value-added millet
products from sorghum, bajra, foxtail millet and finger millet.
The Millet Man of Telangana
He takes up millets in June-July with the onset of the south-west
monsoon. He manages to get a good yield from millets (foxtail millet
3-3.5 quintals/acre, bajra 4-5 quintals/acre, sorghum 4-5 quintals/
acre and finger millet 4-5 quintals/acre) with proper management
practices at the right time even though his village receives meagre
rainfall.
According to Mr. Biradar, millets are super foods for the future
generation because the risk of pest and disease attack is comparatively
low, except for bird damage. He believes a farmer and a jawan are
the two eyes of our country. Keeping the farmer in mind, he started
a Non-Governmental Organization (NGO) called Swayam Shakthi
in Huda Colony, Chandanagar, Hyderabad. The NGO covers 1000
farmers from 8 villages from Sangareddy district. The main purpose
of the NGO is to disseminate timely information to farmers and take
new technologies to the doorstep of the farming community.
"""

# ===============================
# CREATE OR LOAD VECTORSTORE
# ===============================
def create_or_load_vectorstore(text: str):
    if not os.path.exists(CHROMA_DB_PATH):
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    # Load existing DB if available
    if len(os.listdir(CHROMA_DB_PATH)) > 0:
        print("🔄 Loading existing Chroma vector database...")
        embedding_model = OllamaEmbeddings(model="mxbai-embed-large")
        vectordb = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_model)
        return vectordb

    print("📄 Creating new vector database from text...")

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_text(text)

    embedding_model = OllamaEmbeddings(model="mxbai-embed-large")
    vectordb = Chroma.from_texts(
        texts=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )

    print("✅ Vector DB created and saved!")
    return vectordb

# ===============================
# LOCAL RAG TOOL
# ===============================
@tool
def local_rag_tool(query: str) -> str:
    """
    Answer questions ONLY about farmer success stories (e.g., Mr. Biradar, millets, NGO work).
    Example questions:
    - Tell me a story about Mr. Biradar
    - What crops does the Millet Man grow?
    """
    try:
        vectordb = create_or_load_vectorstore(FARMER_TEXT)
        retriever = vectordb.as_retriever(search_kwargs={"k": 5})

        # Ollama local LLM
        llm = OllamaLLM(model="llama3.2:1b")

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=False
        )

        print(f"🔍 Running RAG query: {query}")
        result = qa_chain.invoke({"query": query})
        print("🧠 Raw result:", result)

        answer = result.get("result", "⚠️ No result key in response.")
        return answer or "No relevant information found."

    except Exception as e:
        return f"❌ Error in RAG pipeline: {str(e)}"

# ===============================
# TEST
# ===============================
if __name__ == "__main__":
    query = input("Ask a question about the farmer story: ")
    answer = local_rag_tool.invoke(query)
    print("🤖 Answer:", answer)
