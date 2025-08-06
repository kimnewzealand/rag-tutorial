import streamlit as st
import os
import sys
import time
import psutil
import gc

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_system.core import SimpleRAG

try:
    # Page config
    st.set_page_config(page_title="Compliance Assistant", page_icon="", layout="wide")
except RuntimeError as e:
    if "Runtime instance already exists" in str(e):
        print("⚠️ Streamlit runtime instance already exists! Please run `taskkill /F /IM streamlit.exe 2>nul`")
        sys.exit(1)
    else:
        raise

# Performance monitoring functions
def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def get_storage_size():
    """Get vector database storage size in MB"""
    db_path = "./data/vector_db"
    if os.path.exists(db_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(db_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size / 1024 / 1024
    return 0

def format_time(seconds):
    """Format time in milliseconds or seconds"""
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    return f"{seconds:.2f}s"

# Title
st.title("📋 Compliance Assistant")
st.markdown("Ask questions about the IT compliance agreement")

# Initialize RAG system
@st.cache_resource
def load_rag():
    """Load RAG system with caching"""
    rag = SimpleRAG()
    
    # Create PDF if it doesn't exist
    pdf_path = "data/documents/sample_document.pdf"
    if not os.path.exists(pdf_path):
        st.info("Creating sample PDF...")
        from scripts.create_sample_pdf import create_sample_pdf
        create_sample_pdf()
    
    rag.add_pdf(pdf_path)
    return rag

# Load RAG system
with st.spinner("Loading..."):
    rag = load_rag()

st.success("✅ Ready to search!")

# Performance metrics sidebar
with st.sidebar:
    st.header("📊 Performance Metrics")
    st.write(f"Embedding Model: {rag.embedding_model}")
    # Memory usage
    memory_mb = get_memory_usage()
    st.metric("Memory Usage", f"{memory_mb:.1f} MB")

    
    # Storage size
    storage_mb = get_storage_size()
    st.metric("Storage Size", f"{storage_mb:.1f} MB")
    
    # Refresh button
    if st.button("🔄 Refresh Metrics"):
        st.rerun()

# Search interface
query = st.text_input("Enter your question:", placeholder="Ask about compliance policies...")

if st.button("🔍 Search", type="primary") and query:
    # Performance tracking
    start_time = time.time()
    initial_memory = get_memory_usage()
    
    with st.spinner("Searching..."):
        # Measure embedding and search time
        search_start = time.time()
        results = rag.search(query, 1)
        search_time = time.time() - search_start
        
        # Calculate performance metrics
        total_time = time.time() - start_time
        final_memory = get_memory_usage()
        memory_delta = final_memory - initial_memory
        
        # Display results
        st.subheader("📄 Search Results")
        for i, doc in enumerate(results, 1):
            st.markdown(f"**Result {i}:**")
            st.write(doc)
            st.divider()
        
# Footer
st.markdown("---")
st.markdown("*Powered by ChromaDB and Sentence Transformers*")