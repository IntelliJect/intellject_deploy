🧠 IntelliJect: Smart PYQ-PDF Enhancer
IntelliJect is an intelligent academic tool that uses advanced AI and semantic search to match student notes with relevant Previous Year Questions (PYQs). Built with RAG (Retrieval-Augmented Generation) pipeline for intelligent document analysis and question matching.

🚀 Features
Core Functionality
📄 Smart PDF Processing: Extract and analyze text from uploaded PDF notes using PyMuPDF

🔍 Semantic Search: Find relevant PYQs using OpenAI embeddings and FAISS vector similarity search

🧠 RAG Pipeline: Intelligent question-answer matching using LangChain framework

📚 Multi-Subject Support: Organize and search PYQs across different academic subjects

⚡ Real-time Analysis: Instant matching of note chunks with database questions

🎯 Answer Extraction: AI-powered extraction of specific answers from notes

Technical Features

->PostgreSQL Database: Robust data storage with optimized indexing

->Vector Embeddings: OpenAI embeddings for semantic understanding

->Text Chunking: Intelligent note segmentation using NLTK

->Interactive UI: Clean Streamlit web interface

->Database Health Monitoring: Real-time connection status and diagnostics

📋 Requirements

System Requirements
Python: 3.8 or higher

PostgreSQL: 12+

RAM: Minimum 4GB (8GB recommended for large datasets)

Storage: 1GB+ free space

API Requirements
OpenAI API Key: For GPT-3.5-turbo and embeddings

Database Access: PostgreSQL connection

⚙️ Installation & Setup

1. Clone Repository
bash
git clone https://github.com/IntelliJect/intelliject_hackathon.git
cd intelliject_hackathon

2. Create Virtual Environment
bash
python -m venv intelliject_env
source intelliject_env/bin/activate  # Linux/Mac
# or
intelliject_env\Scripts\activate     # Windows

3. Install Dependencies
bash
pip install -r requirements.txt

4. Download NLTK Data
python
import nltk
nltk.download('punkt')

5. Environment Configuration
Create a .env file in the root directory:
text
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/intelliject
OPENAI_API_KEY=your_openai_api_key_here

6. Database Setup
bash
# Create database tables
python database.py

# Load PYQ data from JSON files
python data_loader.py
7. Run Application
bash
streamlit run main6.py

📁 Project Structure
intelliject/
├── 📄 main6.py              # Main Streamlit application
├── 🗄️ database.py           # Database models and configuration
├── 🧠 rag_pipeline.py       # RAG pipeline and semantic search
├── 📥 data_loader.py        # PYQ data loading utilities
├── 🔧 crud.py              # Database CRUD operations
├── 📋 utils.py             # PDF processing utilities
├── 🏗️ create_tables.py     # Database table creation
├── 📋 requirements.txt     # Python dependencies
├── 🔐 .env                 # Environment variables (create this)
├── 📂 subjects/            # JSON files containing PYQs
│   ├── mathematics.json
│   ├── physics.json
│   └── chemistry.json
└── 📖 README.md            # This file

🗄️ Database Schema
CREATE TABLE pyqs (
    id INTEGER PRIMARY KEY,
    question TEXT NOT NULL,
    subject VARCHAR NOT NULL,
    sub_topic VARCHAR,
    year INTEGER,
    marks FLOAT,
    
    -- Indexes for optimized queries
    INDEX idx_pyqs_subject (subject),
    INDEX idx_pyqs_sub_topic (sub_topic),
    INDEX idx_pyqs_year (year)
);

1. Start the Application
bash
streamlit run main6.py

2. Upload PDF Notes
-Click "Choose PDF file" in the sidebar
-Upload your academic notes in PDF format

3. Select Subject
-Choose the relevant subject from the dropdown
-System will filter PYQs accordingly

4. View Results
-System automatically chunks your notes
-Shows matched PYQs with relevance scores
-Extracts specific answers from your notes

5. Monitor System Health
-Check database connection status in sidebar
-View processing statistics and diagnostics

🤝 Contributing

1.Fork the repository
2.Create a feature branch (git checkout -b feature/AmazingFeature)
3.Commit your changes (git commit -m 'Add some AmazingFeature')
4.Push to the branch (git push origin feature/AmazingFeature)
5.Open a Pull Request
Development Guidelines

-Follow PEP 8 style guidelines
-Add docstrings to all functions
-Include unit tests for new features
-Update README.md for significant changes

🐛 Troubleshooting
Common Issues
Database Connection Error

bash
# Check PostgreSQL service status
sudo service postgresql status

# Verify database exists
psql -U postgres -l
OpenAI API Key Issues

-Ensure API key is valid and has sufficient credits

-Check .env file formatting

PDF Processing Errors

-Ensure uploaded PDFs contain extractable text
-Check file size limits (Streamlit default: 200MB)

📊 Performance Metrics
-PDF Processing: ~1-2 seconds per page

-Semantic Search: ~0.5-1 second per query

-Database Queries: ~50ms average response time

-Memory Usage: ~2-4GB with typical datasets

🔒 Security Notes
->Store OpenAI API keys securely in environment variables

->Use PostgreSQL user accounts with minimal required permissions

->Sanitize user inputs before database operations

->Enable SSL for production database connections

🙏 Acknowledgments
->OpenAI for GPT-3.5-turbo and embedding models
->LangChain for RAG pipeline framework
->Streamlit for the intuitive web interface
->FAISS for efficient vector similarity search
->PostgreSQL for robust data storage

📞 Support
For support, email [aqsa.dishaa17@gmail.com] or create an issue in the GitHub repository.

⭐ Star this repository if you find it helpful! ⭐

Built with ❤️ for students and educators