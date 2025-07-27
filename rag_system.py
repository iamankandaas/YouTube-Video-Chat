# rag_system.py
import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# Set up the language model and embeddings
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2", 
    model_kwargs={'device': 'cpu'} # Use CPU for embeddings
)
def get_transcript(youtube_url):
    """Fetches the transcript for a given YouTube video URL."""
    video_id = youtube_url.split("v=")[1]
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = " ".join([d['text'] for d in transcript_list])
    return transcript

def create_vector_store(transcript):
    """Creates a FAISS vector store from the transcript."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_text(transcript)
    vector_store = FAISS.from_texts(docs, embedding=embeddings)
    return vector_store

def create_rag_chain(vector_store):
    """Creates a RAG chain using LangChain Runnables."""
    retriever = vector_store.as_retriever()

    prompt_template = """Answer the user's question based on the following context:
    {context}
    
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)

    # Creating the chain using LangChain Expression Language (LCEL)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain