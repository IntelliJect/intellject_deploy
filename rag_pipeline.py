import os
from typing import List
from dotenv import load_dotenv

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chat_models import ChatOpenAI
from sqlalchemy.orm import Session
from database import PYQ


# Load environment variables from the .env file
load_dotenv()

# Get OpenAI API key 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embedding = OpenAIEmbeddings()

def load_vectorstore_from_db(session: Session, subject: str = None) -> FAISS:
    """
    Dynamically builds a FAISS vectorstore from PYQs stored in the database for the given subject.
    """
    query_set = session.query(PYQ)
    if subject:
        query_set = query_set.filter(PYQ.subject == subject)

    pyqs = query_set.all()
    if not pyqs:
        return None  # No data to build vector store
    docs = [
    Document(
        page_content=pyq.question,
        metadata={
            "year": pyq.year,
            "subject": pyq.subject,
            "sub_topic": pyq.sub_topic,
            "marks": pyq.marks
        }
    )
    for pyq in pyqs
    ]
    vectorstore = FAISS.from_documents(docs, embedding)
    return vectorstore


def semantic_search_db(session: Session, query: str, subject: str = None, k: int = 5) -> List[Document]:
    """
    Perform semantic search over PYQs stored in the DB using FAISS.
    """
    vectorstore = load_vectorstore_from_db(session, subject)
    if not vectorstore:
        return []

    results = vectorstore.similarity_search(query, k=k)
    return results


def infer_subtopic(text: str) -> str:
    """
    Infer subtopic using OpenAI LLM.
    """
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    prompt = (
        f"Read the following academic content and suggest the most relevant subtopic "
        f"(like 'Firewall', 'Water Pollution', etc.) in 2-3 words:\n\n{text}\n\nSubtopic:"
    )
    try:
        return llm.predict(prompt).strip()
    except Exception as e:
        print("Subtopic inference failed:", e)
        return "General"


def get_relevant_pyqs(session: Session, query: str, subject: str = None, k: int = 3) -> List[Document]:
    """
    Get relevant PYQs from database using semantic similarity search only (no JSON fallback).
    """
    return semantic_search_db(session, query, subject, k)


def nlp_chunk_text(text: str, max_sentences: int = 5) -> List[str]:
    """
    Simple text chunking by sentence count.
    Make sure to call nltk.download('punkt') once in your environment/setup.
    """
    import nltk
    from nltk.tokenize import sent_tokenize

    sentences = sent_tokenize(text)
    chunks = []

    for i in range(0, len(sentences), max_sentences):
        chunk = ' '.join(sentences[i:i + max_sentences])
        chunks.append(chunk)

    return chunks


# def process_notes_and_match_pyqs(text: str, subject: str, session: Session, k: int = 3):

    # """
    # Processes the notes text: chunk, infer subtopic, and get matching PYQs from DB.
    # """
    # chunks = nlp_chunk_text(text)
    # results = []

    # for chunk in chunks:
    #     # subtopic = infer_subtopic(chunk)
    #     # Replace the LLM call with database lookup
    #     if related_qs:
    #         subtopic = related_qs[0].metadata.get('sub_topic', 'General')
    #     else:
    #         subtopic = "No matches found"

    #     matches = get_relevant_pyqs(session, chunk, subject, k=k)
    #     results.append({
    #         "chunk": chunk,
    #         "subtopic": subtopic,
    #         "matches": matches
    #     })

    # return results
    def process_notes_and_match_pyqs(text: str, subject: str, session: Session, k: int = 3):
        chunks = nlp_chunk_text(text)
        results = []
        
        for chunk in chunks:
            # Get matches first
            matches = get_relevant_pyqs(session, chunk, subject, k=k)
            
            # Then extract subtopic from database results
            if matches:
                subtopic = matches[0].metadata.get('sub_topic', 'General')
            else:
                subtopic = "No matches found"
                
            results.append({
                "chunk": chunk,
                "subtopic": subtopic,
                "matches": matches
            })
        return results

