from sqlalchemy import create_engine, Column, Integer, String, DateTime, Index, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import datetime
import os

# Load environment variables from .env
load_dotenv()

# Create the full database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Setup engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Declare Base
Base = declarative_base()

class PYQ(Base):
    __tablename__ = "pyqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)  # Use Text for longer questions
    subject = Column(String, nullable=False)
    sub_topic = Column(String)
    year = Column(Integer)
    marks = Column(Float)  # Supports decimal marks like 2.5

    __table_args__ = (
        Index("idx_pyqs_subject", "subject"),
        Index("idx_pyqs_sub_topic", "sub_topic"),
        Index("idx_pyqs_year", "year"),
    )

    def __repr__(self):  
        return (
            f"<PYQ(id={self.id}, subject='{self.subject}', "
            f"sub_topic='{self.sub_topic}', year={self.year}, marks={self.marks})>"
        )

# Function to create all tables
def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("Tables created:")
        print("- pdf_history")
        print("- pyqs (without difficulty column)")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

# Function to get database session
def get_db():
    """Get database session for dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize tables on import (optional)
if __name__ == "__main__":  
    create_tables()
