# =========================================
# 📚 RAG PIPELINE (Text + OpenAI + Chroma + PDF)
# =========================================
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.tools import tool
from PyPDF2 import PdfReader
import os

# ===============================
# CONFIG
# ===============================
CHROMA_DB_PATH = "C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/openai_chroma_db"
PDF_PATH = "C:/Users/MUTHU/Documents/aproj/profarm-backend/profarmai/app/src/agents/Success-Stories-Farmers.pdf"

# Set your OpenAI API key (ensure you’ve set it in your environment)
# e.g., setx OPENAI_API_KEY "your-api-key"
from dotenv import load_dotenv
load_dotenv()

# ===============================
# HELPER – Read PDF
# ===============================
def read_pdf_text(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ PDF not found: {pdf_path}")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()
# ===============================
# INITIALIZE VECTORSTORE (ONCE)
# ===============================
def initialize_vectorstore() -> Chroma:
    """Creates or loads a persistent Chroma vector database."""
    if not os.path.exists(CHROMA_DB_PATH):
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

    # If Chroma DB already exists — just load it
    if len(os.listdir(CHROMA_DB_PATH)) > 0:
        print("🔄 Loading existing Chroma vector database...")
        return Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_model)

    # Otherwise, create new DB
    print("📄 Creating new vector database from PDF...")
    text = read_pdf_text(PDF_PATH)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(text)

    vectordb = Chroma.from_texts(
        texts=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )
    print("✅ Vector DB created and saved!")
    return vectordb

GLOBAL_VECTORDb = initialize_vectorstore()
'''
# ===============================
# CREATE OR LOAD VECTORSTORE
# ===============================
def create_or_load_vectorstore(pdf_path: str):
    if not os.path.exists(CHROMA_DB_PATH):
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

    # Load existing DB if available
    if len(os.listdir(CHROMA_DB_PATH)) > 0:
        print("🔄 Loading existing Chroma vector database...")
        vectordb = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_model)
        return vectordb

    print("📄 Creating new vector database from PDF...")

    # Read and split text
    text = read_pdf_text(pdf_path)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_text(text)

    vectordb = Chroma.from_texts(
        texts=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )

    print("✅ Vector DB created and saved!")
    return vectordb
'''
# ===============================
# RAG TOOL
# ===============================
@tool
def local_rag_tool(query: str) -> str:
    """
    Use this tool when the user asks questions about **Indian farmers,
    success stories, case studies, sustainable agriculture practices, 
    crop yields, or individual farmer achievements** that are stored in a local PDF.
    """
    try:
        retriever = GLOBAL_VECTORDb.as_retriever(search_kwargs={"k": 5})

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

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
    query = input("Ask a question about the farmer success stories: ")
    answer = openai_rag_tool.invoke(query)
    print("🤖 Answer:", answer)
