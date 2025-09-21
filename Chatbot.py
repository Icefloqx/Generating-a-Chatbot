import os
import gradio as gr

# LangChain imports
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Configuration
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

# Use HuggingFace embeddings
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Connect to Chroma DB
vector_store = Chroma(
    collection_name="sample_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

# Init Groq LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",  
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.5
)

#Retriever
num_results = 5
retriever = vector_store.as_retriever(search_kwargs={'k': num_results})

# Chatbot response function

def stream_response(message, history):
    # retrieve relevant chunks
    docs = retriever.invoke(message)

    # combine chunks into knowledge base
    knowledge = "\n\n".join([doc.page_content for doc in docs])

    # RAG-style prompt
    rag_prompt = f"""
    You are an assistant that answers questions based ONLY on the knowledge provided.
    Do not use internal knowledge. Do not mention the phrase "knowledge base" or "documents."

    Question: {message}

    Conversation history: {history}

    Knowledge:
    {knowledge}
    """

    print(rag_prompt)  #debug

    # stream Groq response
    partial_message = ""
    for response in llm.stream(rag_prompt):
        partial_message += response.content
        yield partial_message


#Gradio Chat Interface
chatbot = gr.ChatInterface(
    stream_response,
    textbox=gr.Textbox(
        placeholder="Ask me anything from your PDF...",
        container=False,
        autoscroll=True,
        scale=7,
    ),
)

#Launch App                  
if __name__ == "__main__":
    chatbot.launch()
