import streamlit as st
from config import Config
from utils import process_text_into_chunks, get_pdf_text
from vector_store import initialize_vectorstore
from rag_engine import RAGEngine

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Mini RAG Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Import beautiful fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Variables */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --accent-blue: #4a9eff;
        --accent-purple: #9d7bea;
        --accent-pink: #ff6b9d;
        --bg-dark: #0a0e27;
        --bg-card: #151b3d;
        --bg-card-hover: #1a2049;
        --text-primary: #f0f4f8;
        --text-secondary: #a8b2d1;
        --text-muted: #64748b;
        --border-color: #2d3561;
        --success-green: #10b981;
        --warning-orange: #f59e0b;
        --error-red: #ef4444;
    }
    
    /* Main Background */
    .stApp {
        background: var(--bg-dark);
        font-family: 'Outfit', sans-serif;
        color: var(--text-primary);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #151b3d 0%, #0d1128 100%);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: var(--text-primary);
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    /* Title Styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem !important;
        animation: fadeInDown 0.8s ease-out;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* Cards and Containers */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Text Input & Text Area */
    .stTextArea textarea,
    .stTextInput input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: var(--accent-purple) !important;
        box-shadow: 0 0 0 3px rgba(157, 123, 234, 0.15) !important;
        outline: none !important;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: var(--bg-card);
        border: 2px dashed var(--border-color);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-purple);
        background: var(--bg-card-hover);
    }
    
    /* Radio Buttons */
    .stRadio > div {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 0.75rem;
        border: 1px solid var(--border-color);
    }
    
    .stRadio label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    
    .stRadio label:hover {
        background: var(--bg-card-hover);
        color: var(--text-primary) !important;
    }
    
    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: slideInLeft 0.4s ease-out;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stChatMessage"]:hover {
        border-color: var(--accent-purple);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    /* Chat Input */
    [data-testid="stChatInput"] {
        background: var(--bg-card);
        border: 2px solid var(--border-color);
        border-radius: 16px;
        padding: 0.5rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent-purple);
        box-shadow: 0 0 0 4px rgba(157, 123, 234, 0.15);
    }
    
    /* Success/Warning/Error Boxes */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
        border-left: 4px solid var(--success-green);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: var(--text-primary);
        animation: slideInLeft 0.5s ease-out;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-left: 4px solid var(--warning-orange);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: var(--text-primary);
        animation: slideInLeft 0.5s ease-out;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
        border-left: 4px solid var(--error-red);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: var(--text-primary);
        animation: slideInLeft 0.5s ease-out;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        color: var(--text-primary) !important;
        font-weight: 500;
        padding: 1rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-card-hover);
        border-color: var(--accent-purple);
    }
    
    .streamlit-expanderContent {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 1.5rem;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 2rem 0;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--accent-purple) transparent transparent transparent !important;
    }
    
    /* Caption/Small Text */
    .stCaption {
        color: var(--text-muted) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }
    
    /* Markdown in Messages */
    [data-testid="stChatMessage"] p {
        color: var(--text-primary);
        line-height: 1.7;
        font-size: 1rem;
    }
    
    [data-testid="stChatMessage"] code {
        background: rgba(102, 126, 234, 0.1);
        color: var(--accent-blue);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 100px;
        font-size: 0.9rem;
        font-weight: 500;
        animation: fadeIn 0.6s ease-out;
    }
    
    .status-badge.active {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%);
        border-color: var(--success-green);
        color: var(--success-green);
    }
    
    .status-badge.empty {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-color: var(--warning-orange);
        color: var(--warning-orange);
    }
    
    /* Pulse Animation for Status */
    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: currentColor;
        animation: pulse 2s infinite;
    }
    
    /* Source Card in Expander */
    .streamlit-expanderContent blockquote {
        background: rgba(102, 126, 234, 0.05);
        border-left: 3px solid var(--accent-purple);
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        color: var(--text-secondary);
        font-style: normal;
    }
    
    /* Headers in sidebar */
    [data-testid="stSidebar"] h2 {
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Subtle glow effect */
    .glow {
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
Config.validate_keys()

# Initialize Session State
if "vectorstore" not in st.session_state:
    with st.spinner("🔮 Connecting to Vector Database..."):
        st.session_state.vectorstore = initialize_vectorstore()

# Track what is currently indexed
if "current_source" not in st.session_state:
    st.session_state.current_source = "Empty"

# --- SIDEBAR: INPUT ---
with st.sidebar:
    st.markdown("## 📂 Source Material")
    st.markdown("Upload your knowledge base")
    
    input_method = st.radio(
        "Choose Input Method:",
        ["Paste Text", "Upload File"],
        label_visibility="collapsed"
    )
    
    raw_text = ""
    source_name = ""

    if input_method == "Paste Text":
        raw_text = st.text_area(
            "Enter your text here:",
            height=300,
            placeholder="Paste your document, article, or any text you want to query..."
        )
        if raw_text:
            source_name = "User Input Text"
    else:
        uploaded_file = st.file_uploader(
            "Upload Document",
            type=["txt", "pdf"],
            help="Supported formats: TXT, PDF"
        )
        if uploaded_file:
            source_name = uploaded_file.name
            if uploaded_file.type == "application/pdf":
                raw_text = get_pdf_text(uploaded_file)
            else:
                raw_text = uploaded_file.read().decode("utf-8")
    
    # Sidebar info
    st.markdown("---")
    st.markdown("### 💡 How It Works")
    st.markdown("""
    1. **Upload** your document or paste text
    2. **Ask** questions naturally
    3. **Get** AI-powered answers with sources
    """)

# --- AUTO-INGESTION LOGIC ---
if raw_text and source_name and source_name != st.session_state.current_source:
    with st.spinner(f"⚡ Processing '{source_name}'..."):
        try:
            # 1. Chunk and Process
            docs = process_text_into_chunks(raw_text, source_name)
            
            # 2. Add to Vector Store
            st.session_state.vectorstore.add_documents(docs)
            
            # 3. Update State
            st.session_state.current_source = source_name
            st.toast(f"✅ Successfully indexed {len(docs)} chunks!", icon="✅")
            
        except Exception as e:
            st.error(f"❌ Indexing failed: {e}")

# --- MAIN: INTERFACE ---
st.markdown("# 🧠 Mini RAG")
st.markdown("### Intelligent Document Q&A System")

# Status Indicator with custom styling
col1, col2 = st.columns([3, 1])

with col1:
    if st.session_state.current_source == "Empty":
        st.markdown(
            '<div class="status-badge empty"><span class="pulse-dot"></span>No knowledge base loaded</div>',
            unsafe_allow_html=True
        )
        st.info("👈 Upload a document or paste text in the sidebar to get started")
    else:
        st.markdown(
            f'<div class="status-badge active"><span class="pulse-dot"></span>Active Knowledge Base: <strong>{st.session_state.current_source}</strong></div>',
            unsafe_allow_html=True
        )

st.markdown("---")

# Chat Interface
query = st.chat_input("💬 Ask anything about your documents...")

if query:
    if st.session_state.current_source == "Empty":
        st.error("⚠️ Please provide a document or text before asking questions.")
    else:
        # Display User Query
        with st.chat_message("user", avatar="👤"):
            st.markdown(query)

        # Process Query
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🔍 Searching knowledge base..."):
                try:
                    engine = RAGEngine(st.session_state.vectorstore)
                    result = engine.query(query)
                    
                    if result:
                        st.markdown(result["answer"])
                        
                        # Metrics Footer
                        col1, col2, col3 = st.columns([2, 2, 3])
                        with col1:
                            st.caption(f"⏱️ Response Time: **{result['metrics']['latency']}s**")
                        with col2:
                            st.caption(f"💰 Cost: **${result['metrics']['cost']}**")
                        with col3:
                            st.caption(f"📊 Sources Used: **{len(result['sources'])}**")
                        
                        # Sources
                        with st.expander("📚 View Cited Sources", expanded=False):
                            for i, doc in enumerate(result["sources"]):
                                st.markdown(f"**[{i+1}] {doc.metadata.get('source', 'Unknown Source')}**")
                                st.markdown(f"> {doc.page_content}")
                                if i < len(result["sources"]) - 1:
                                    st.divider()
                    else:
                        st.warning("🔍 No relevant information found in the knowledge base.")
                        
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: var(--text-muted); font-size: 0.85rem; font-family: \'JetBrains Mono\', monospace;">Made by Niwesh Sah</p>',
    unsafe_allow_html=True
)