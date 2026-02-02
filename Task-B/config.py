import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")

    # Pinecone Settings
    INDEX_NAME = "mini-rag-index"
    NAMESPACE = "demo-namespace"
    EMBEDDING_DIMENSION = 768
    CLOUD_PROVIDER = "aws"
    REGION = "us-east-1"

    # Models
    EMBEDDING_MODEL = "models/text-embedding-004"
    LLM_MODEL = "gemini-2.5-flash"
    RERANKER_MODEL = "rerank-english-v3.0"

    @staticmethod
    def validate_keys():
        """Checks if all required API keys are present."""
        missing_keys = []
        if not Config.GOOGLE_API_KEY: missing_keys.append("GOOGLE_API_KEY")
        if not Config.PINECONE_API_KEY: missing_keys.append("PINECONE_API_KEY")
        if not Config.COHERE_API_KEY: missing_keys.append("COHERE_API_KEY")
        
        if missing_keys:
            st.error(f"❌ Missing API Keys in .env: {', '.join(missing_keys)}")
            st.stop()