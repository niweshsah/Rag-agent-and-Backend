import streamlit as st
from config import Config
from utils import process_text_into_chunks, get_pdf_text
from vector_store import initialize_vectorstore
from rag_engine import RAGEngine

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mini RAG Pro", layout="wide")

# --- INITIALIZATION ---
Config.validate_keys()

# Initialize Session State
if "vectorstore" not in st.session_state:
    with st.spinner("Connecting to Vector Database..."):
        st.session_state.vectorstore = initialize_vectorstore()

# Track what is currently indexed
if "current_source" not in st.session_state:
    st.session_state.current_source = "Empty"

# --- SIDEBAR: INPUT ---
with st.sidebar:
    st.header("📂 1. Source Material")
    
    input_method = st.radio("Choose Input:", ["Paste Text", "Upload File"])
    
    raw_text = ""
    source_name = ""

    if input_method == "Paste Text":
        raw_text = st.text_area("Enter text here:", height=300)
        if raw_text:
            source_name = "User Input Text"
    else:
        uploaded_file = st.file_uploader("Upload document", type=["txt", "pdf"])
        if uploaded_file:
            source_name = uploaded_file.name
            if uploaded_file.type == "application/pdf":
                raw_text = get_pdf_text(uploaded_file)
            else:
                raw_text = uploaded_file.read().decode("utf-8")

# --- AUTO-INGESTION LOGIC (Runs Immediately) ---
# We check this BEFORE waiting for a query
if raw_text and source_name and source_name != st.session_state.current_source:
    with st.spinner(f"⚡ Processing '{source_name}'..."):
        try:
            # 1. Chunk and Process
            docs = process_text_into_chunks(raw_text, source_name)
            
            # 2. Add to Pinecone
            # Note: You might want to delete old docs here if you want strict 1-doc mode:
            # st.session_state.vectorstore.delete(delete_all=True)
            
            st.session_state.vectorstore.add_documents(docs)
            
            # 3. Update State
            st.session_state.current_source = source_name
            st.toast(f"Successfully indexed {len(docs)} chunks!", icon="✅")
            
        except Exception as e:
            st.error(f"Indexing failed: {e}")

# --- MAIN: INTERFACE ---
st.title("🤖 Mini RAG: Auto-Ingest")

# Status Indicator
if st.session_state.current_source == "Empty":
    st.warning("⚠️ RAG is empty. Please upload a file or paste text in the sidebar.")
else:
    st.success(f"🧠 RAG Knowledge Base: **{st.session_state.current_source}**")

st.markdown("---")

# Chat Interface
query = st.chat_input("Ask a question about your documents...")

if query:
    if st.session_state.current_source == "Empty":
        st.error("Please provide text or a file before asking a question.")
    else:
        # Display User Query
        with st.chat_message("user"):
            st.write(query)

        # Process Query
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    engine = RAGEngine(st.session_state.vectorstore)
                    result = engine.query(query)
                    
                    if result:
                        st.markdown(result["answer"])
                        
                        # Metrics Footer
                        st.caption(f"⏱️ {result['metrics']['latency']}s | 💰 {result['metrics']['cost']}")
                        
                        # Sources
                        with st.expander("📚 View Cited Sources"):
                            for i, doc in enumerate(result["sources"]):
                                st.markdown(f"**[{i+1}] {doc.metadata.get('source', 'Unknown')}**")
                                st.markdown(f"> {doc.page_content}")
                                st.divider()
                    else:
                        st.warning("No relevant information found.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {e}")