import streamlit as st
import time
import os
from dotenv import load_dotenv

# LangChain Imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from langchain_cohere import CohereRerank
from langchain_classic.retrievers.contextual_compression import (
    ContextualCompressionRetriever,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec

# Load Environment Variables
load_dotenv()

# --- CONFIGURATION ---
INDEX_NAME = "mini-rag-index"
NAMESPACE = "demo-namespace"

# --- INIT SESSION STATE ---
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# --- SETUP TITLE & SIDEBAR ---
st.set_page_config(page_title="Mini RAG with Citations", layout="wide")
st.title("🤖 Mini RAG: Gemini + Pinecone + Cohere Rerank")
st.markdown(
    "Retrieval-Augmented Generation with **Reranking** and **Inline Citations**."
)

# --- HELPER FUNCTIONS ---


def get_embeddings():
    """Initialize Google Generative AI Embeddings"""
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")


def setup_vectorstore():
    """Initialize Pinecone Vector Store"""
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    # Create index if not exists (check list of indexes first)
    existing_indexes = [i.name for i in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=INDEX_NAME,
            dimension=768,  # Dimension for text-embedding-004
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    embeddings = get_embeddings()
    vectorstore = PineconeVectorStore(
        index_name=INDEX_NAME, embedding=embeddings, namespace=NAMESPACE
    )
    return vectorstore


def process_text(text, source_name):
    """
    Chunking Strategy: 1000 characters, 100 characters overlap
    Creates documents with metadata for citations
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_text(text)

    # Create Documents with Metadata for Citations
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "source": source_name,
                "chunk_id": i,
                "text_preview": chunk[:50] + "...",
            },
        )
        documents.append(doc)
    return documents


# --- SIDEBAR: DATA INGESTION ---
with st.sidebar:
    st.header("1. Ingestion")
    user_txt = st.text_area("Paste Text Here", height=200)
    uploaded_file = st.file_uploader("Or Upload .txt", type="txt")

    if st.button("Ingest Data"):
        with st.spinner("Chunking, Embedding, and Upserting..."):
            try:
                # Prepare Data
                raw_text = ""
                source = "User Input"

                if uploaded_file:
                    raw_text = uploaded_file.read().decode("utf-8")
                    source = uploaded_file.name
                elif user_txt:
                    raw_text = user_txt

                if not raw_text:
                    st.error("Please provide text.")
                else:
                    # Initialize VectorStore
                    if st.session_state.vectorstore is None:
                        st.session_state.vectorstore = setup_vectorstore()

                    # Process text into chunks
                    docs = process_text(raw_text, source)

                    # Upsert to Pinecone
                    st.session_state.vectorstore.add_documents(docs)
                    st.success(f"✅ Indexed {len(docs)} chunks to Pinecone!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# --- MAIN: RAG PIPELINE ---
st.header("2. RAG Query")
query = st.text_input("Ask a question about the uploaded text:")

if query:
    start_time = time.time()

    try:
        # 1. RETRIEVER setup
        if st.session_state.vectorstore is None:
            st.session_state.vectorstore = setup_vectorstore()

        base_retriever = st.session_state.vectorstore.as_retriever(
            search_type="mmr",  # Maximal Marginal Relevance for diversity
            search_kwargs={"k": 10},  # Fetch more docs initially for reranking
        )

        # 2. RERANKER (Cohere)
        compressor = CohereRerank(top_n=3, model="rerank-english-v3.0")
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=base_retriever
        )

        # 3. GENERATION
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            convert_system_message_to_human=True,
        )

        # Prompt with Citation Instructions
        template = """You are a helpful assistant. Answer the question based ONLY on the following context.

If you cannot answer the question based on the context, say "I cannot answer this based on the provided context."

You must cite your sources. Refer to the context chunks using their index numbers like [1], [2], etc.
At the end of each sentence where you use information, add the citation.

Context:
{context}

Question: {question}

Answer:"""

        prompt = ChatPromptTemplate.from_template(template)

        # Retrieve Documents (Reranked)
        retrieved_docs = compression_retriever.invoke(query)

        if not retrieved_docs:
            st.warning("No relevant documents found. Please ingest some data first.")
        else:
            # Format context with explicit IDs for the LLM to reference
            formatted_context = "\n\n".join(
                f"[{i + 1}] {doc.page_content}" for i, doc in enumerate(retrieved_docs)
            )

            # Generate Answer
            chain = prompt | llm
            response = chain.invoke({"context": formatted_context, "question": query})

            end_time = time.time()

            # --- DISPLAY RESULTS ---
            st.markdown("### Answer")
            st.write(response.content)

            # Metrics
            total_tokens = len(formatted_context.split()) + len(
                query.split()
            )  # Rough estimate
            cost_estimate = (
                total_tokens / 1000
            ) * 0.0000185  # Rough Gemini-1.5-Flash pricing

            col1, col2 = st.columns(2)
            col1.metric("Latency", f"{round(end_time - start_time, 2)}s")
            col2.metric("Est. Cost", f"${cost_estimate:.6f}")

            # --- CITATIONS / SOURCES SECTION ---
            st.markdown("---")
            st.subheader("📚 Sources (Reranked)")

            for i, doc in enumerate(retrieved_docs):
                relevance_score = doc.metadata.get("relevance_score", "N/A")
                source = doc.metadata.get("source", "Unknown")

                with st.expander(f"Source [{i + 1}] - Score: {relevance_score}"):
                    st.caption(f"**Origin:** {source}")
                    st.markdown(f"> {doc.page_content}")

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
        st.exception(e)  # Show full traceback for debugging
