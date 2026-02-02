import time
from pinecone import Pinecone, ServerlessSpec, PineconeException
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import Config

def get_embeddings():
    """Returns the Google Generative AI Embeddings model."""
    return GoogleGenerativeAIEmbeddings(model=Config.EMBEDDING_MODEL)

def initialize_vectorstore():
    """
    Initializes and returns the Pinecone VectorStore.
    Creates the index if it doesn't exist.
    """
    try:
        pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        
        # Check if index exists, create if not
        existing_indexes = [i.name for i in pc.list_indexes()]
        
        if Config.INDEX_NAME not in existing_indexes:
            pc.create_index(
                name=Config.INDEX_NAME,
                dimension=Config.EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud=Config.CLOUD_PROVIDER, region=Config.REGION)
            )
            # Wait a moment for index initialization
            time.sleep(1)

        embeddings = get_embeddings()
        
        vectorstore = PineconeVectorStore(
            index_name=Config.INDEX_NAME,
            embedding=embeddings,
            namespace=Config.NAMESPACE
        )
        return vectorstore

    except PineconeException as e:
        raise ConnectionError(f"Failed to connect to Pinecone: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during VectorStore setup: {str(e)}")