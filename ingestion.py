from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from uuid import uuid4
from dotenv import load_dotenv
import os


#Import the .env file
from dotenv import load_dotenv
load_dotenv()

#Configure the api and the path
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

#Initiate the embeddings
embeddings_model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#initiate the vectore store
vector_store = Chroma(
    collection_name="sample_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

#load the pdf document
loader = PyPDFDirectoryLoader(DATA_PATH)

raw_documents= loader.load()

#Splitting documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=150,
    length_function=len,
    is_separator_regex=False,
)

#Creating chunks
chunks=text_splitter.split_documents(raw_documents)

#creating unique ids
#uuids = [str(uuid4()) for _ in range(len(chunks))]

#adding chunks to vector store
vector_store.add_documents(documents=chunks)

#initiate the llm(brain)
llm=ChatGroq(
    model="llama-3.1-8b-instant",  
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)
