import io
import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def get_pdf_text(uploaded_file):
    """
    Extracts text from a Streamlit UploadedFile object (PDF).
    """
    try:
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        raise ValueError(f"Error reading PDF: {e}")

def process_text_into_chunks(text: str, source_name: str) -> list[Document]:
    """
    Splits text into chunks of 1000 characters with 100 overlap.
    """
    if not text:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_text(text)
    
    documents = [
        Document(
            page_content=chunk,
            metadata={
                "source": source_name,
                "chunk_id": i,
                "text_preview": chunk[:50] + "..."
            }
        ) for i, chunk in enumerate(chunks)
    ]
    
    return documents