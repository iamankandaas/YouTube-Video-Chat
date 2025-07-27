import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Import the library and its exceptions
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Load environment variables
load_dotenv()

# Set up the models
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.2)
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2", 
    model_kwargs={'device': 'cpu'}
)

def get_transcript(youtube_url):
    """
    Fetches the transcript using the instance-based fetch() method that you proved works.
    """
    try:
        video_id = youtube_url.split("v=")[1].split("&")[0]        
        ytt_api = YouTubeTranscriptApi()        
        transcript_chunks = ytt_api.fetch(video_id)
        transcript = " ".join([chunk.text for chunk in transcript_chunks])
        
        if not transcript:
             raise Exception("Transcript was found but was empty.")
             
        return transcript
        
    except (TranscriptsDisabled, NoTranscriptFound):
        raise Exception("No English transcript was found for this video.")
    except Exception as e:
        raise Exception(f"An error occurred while fetching the transcript: {e}")


def create_vector_store(transcript):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs_as_strings = text_splitter.split_text(transcript)
    vector_store = FAISS.from_texts(docs_as_strings, embedding=embeddings)
    return vector_store

def create_rag_chain(vector_store):
    retriever = vector_store.as_retriever()
    prompt_template = """Answer the user's question based ONLY on the following context:
    If the answer is not found in the context, say "I don't have enough information from the video to answer that."
    Context: {context}
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain