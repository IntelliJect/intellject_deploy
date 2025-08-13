import streamlit as st
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from database import engine, SessionLocal,PYQ
from utils import extract_text_from_pdf
from rag_pipeline import get_relevant_pyqs
import tempfile
import datetime
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from nltk.tokenize import sent_tokenize
from langchain.chat_models import ChatOpenAI

st.set_page_config(page_title="IntelliJect", layout="wide")
st.title("🧠 IntelliJect: Intelligent Integration of PYQ's into Notes")

st.markdown("""
    <style>
    .question-card {
        background-color: #283250;
        color: #d6f5e3 !important;
        border-radius: 6px;
        padding: 10px 12px;
        margin: 10px 0 6px 0;
        font-size: 15px;
    }
    .highlight-answer {
        display: inline-block;
        background: #ffe44d;
        color: #232323 !important;
        border-radius: 5px;
        padding: 2px 6px;
        margin: 6px 0 2px 0;
        font-weight: 600;
        font-family: 'Georgia', serif;
        font-size: 15px;
    }
    .database-subtopic {
        background-color: #e8f5e8;
        color: #2d5a2d !important;
        border-radius: 4px;
        padding: 4px 8px;
        font-weight: bold;
    }
    .error-box {
        background-color: #ffebee;
        color: #d32f2f;
        padding: 10px;
        border-radius: 4px;
        border-left: 4px solid #d32f2f;
    }
    </style>
""", unsafe_allow_html=True)

def extract_answer_from_chunk(chunk, question):
    prompt = f"""
Given the following notes and a question, extract the exact sentence(s) from the notes that directly answer the question if possible. Only return the excerpt(s), not any explanation.

Notes:
\"\"\"{chunk}\"\"\"

Question:
\"\"\"{question}\"\"\"

Answer/excerpt:
"""
    try:
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        answer = llm.predict(prompt).strip()
        return answer
    except Exception as e:
        st.error(f"Error extracting answer: {e}")
        return ""

# Test database connection function
def test_database_connection():
    try:
        with SessionLocal() as db:
            # Test basic query
            result = db.execute(text("SELECT 1")).fetchone()
            if result:
                return True, "Database connection successful"
            else:
                return False, "Database query returned no result"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"

# Enhanced sidebar with detailed diagnostics
with st.sidebar:
    st.header("🔧 System Status")
    
    # Database connection test
    db_status, db_message = test_database_connection()
    if db_status:
        st.success(f"✅ {db_message}")
    else:
        st.error(f"❌ {db_message}")
        st.markdown(f"<div class='error-box'>Database connection failed. Please check your database configuration.</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📑 Upload your notes PDF", type=["pdf"])
with col2:
    subject = st.selectbox("📚 Select Subject", ["Cyber Security", "Environmental Sciences","Probability and Statistics"])

# Only show button if database is connected
if not db_status:
    st.error("❌ Cannot proceed - database connection failed. Please check your database setup.")
    st.stop()

if uploaded_file and subject:
    match_button = st.button("🔍 Match PYQs", type="primary", use_container_width=True)
    
    if not match_button:
        st.info("👆 Click 'Match PYQs' to process your PDF and find relevant questions.")
        st.stop()

if uploaded_file and subject:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_pdf_path = tmp_file.name

    # Simple file info display (no database saving)
    st.success(f"✅ PDF '{uploaded_file.name}' loaded for processing.")

    st.subheader("📑 Extracting and Chunking Notes...")
    
    try:
        text_chunks = extract_text_from_pdf(tmp_pdf_path)
    except Exception as e:
        st.error(f"❌ Could not extract content from PDF: {e}")
        st.stop()

    if not text_chunks:
        st.error("❌ Could not extract content from the PDF.")
        st.stop()
    else:
        st.success(f"✅ Successfully extracted {len(text_chunks)} chunks.")

        # Test subject data availability
        try:
            with SessionLocal() as db:
                subject_count = db.query(PYQ).filter(PYQ.subject == subject).count()
                if subject_count == 0:
                    st.error(f"❌ No PYQs found for subject '{subject}' in database.")
                    
                    # Show available subjects for debugging
                    available_subjects = db.execute(text("SELECT DISTINCT subject FROM pyqs")).fetchall()
                    if available_subjects:
                        subjects_list = [subj[0] for subj in available_subjects]
                        st.info(f"Available subjects in database: {', '.join(subjects_list)}")
                    st.stop()
                else:
                    st.info(f"📚 Found {subject_count} PYQs for subject: {subject}")
        except Exception as e:
            st.error(f"❌ Could not check subject data: {e}")
            st.stop()

        try:
            pdf_doc = fitz.open(tmp_pdf_path)
            num_pages = pdf_doc.page_count
        except Exception as e:
            st.error(f"❌ Could not open PDF with PyMuPDF: {e}")
            st.stop()

        if len(text_chunks) != num_pages:
            st.warning(f"⚠️ Number of text chunks ({len(text_chunks)}) does not match number of PDF pages ({num_pages}). Highlighting may be inaccurate.")

        # Process chunks
        for i, chunk in enumerate(text_chunks):  # Process ALL chunks
            col_img, col_pyqs = st.columns([1.5, 1])
            answers_to_highlight = []

            with col_pyqs:
                st.markdown(f"### 📄 Page {i+1}")
                
                try:
                    with SessionLocal() as session:
                        related_qs = get_relevant_pyqs(session, chunk, subject)
                        
                        if related_qs:
                            subtopic = related_qs[0].metadata.get('sub_topic', 'General')
                            st.markdown(
                                f"<span style='font-size:18px;font-weight:bold;'>🔎 Subtopic: "
                                f"<span class='database-subtopic'>{subtopic}</span></span>", 
                                unsafe_allow_html=True
                            )
                        else:
                            subtopic = "No matches found"
                            st.markdown(
                                f"<span style='font-size:18px;font-weight:bold;'>🔎 Subtopic: {subtopic}</span>", 
                                unsafe_allow_html=True
                            )
                            
                except Exception as e:
                    st.error(f"❌ Database query failed: {e}")
                    related_qs = []

                if related_qs:
                    for idx, q in enumerate(related_qs[:3]):  # Limit to 3 questions per chunk
                        answer_text = extract_answer_from_chunk(chunk, q.page_content)
                        if answer_text:
                            for sent in sent_tokenize(answer_text):
                                sent_clean = sent.strip()
                                if sent_clean:
                                    answers_to_highlight.append(sent_clean)

                        st.markdown(
                            f"<div class='question-card'>"
                            f"❓ <b>Q{idx+1}:</b> {q.page_content}<br>"
                            f"<span style='font-size:14px;opacity:0.8;'>"
                            f"🧩 Topic: {q.metadata.get('sub_topic', 'N/A')} | "
                            f"📝 Marks: {q.metadata.get('marks', 'N/A')} | "
                            f"📅 {q.metadata.get('year', 'N/A')}"
                            f"</span><br>"
                            f"<span class='highlight-answer'><b>📌 Answer:</b> {answer_text if answer_text else '(No direct answer found)'}</span>"
                            f"</div>", unsafe_allow_html=True
                        )
                        st.markdown("---", unsafe_allow_html=True)
                else:
                    st.info("❗ No relevant PYQs found for this chunk.")

            with col_img:
                try:
                    if i >= num_pages:
                        st.warning(f"Chunk index {i} out of PDF pages range ({num_pages}). Skipping highlighting.")
                        continue
                        
                    page = pdf_doc[i]

                    # RESTORED PDF HIGHLIGHTING FUNCTIONALITY
                    highlight_count = 0
                    

                    # Convert  page to image
                    pix = page.get_pixmap(dpi=150)
                    img_data = pix.pil_tobytes(format="PNG")
                    img = Image.open(BytesIO(img_data))
                    
                    # Display with highlight count
                    st.image(img, caption=f"PDF Page {i+1} ", use_container_width=True)
                    
                    if highlight_count > 0:
                        st.success()

                except Exception as e:
                    st.warning(f"Could not render PDF page {i+1}: {e}")
                    # Fallback: show text content if PDF rendering fails
                    st.text_area(f"Page {i+1} Text Content", chunk[:500] + "...", height=300)

        

        # Clean up
        try:
            pdf_doc.close()
            import os
            os.unlink(tmp_pdf_path)
        except:
            pass


