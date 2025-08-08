import streamlit as st
import os
import sys
import time
import psutil
import gc
from create_sample_pdf import create_sample_pdf
from rag_system.core import SimpleRAG
# Check SQLite version for compatibility
import sqlite3
version = sqlite3.sqlite_version
print(f"📊 SQLite version: {version}")

# ChromaDB 0.3.29 works with older SQLite versions
if version < "3.35.0":
    print("⚠️ Using ChromaDB 0.3.29 for compatibility with older SQLite")
else:
    print("✅ SQLite version is compatible with newer ChromaDB versions")


# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

try:
    # Page config
    st.set_page_config(page_title="Compliance Assistant", page_icon="", layout="wide")
except RuntimeError as e:
    if "Runtime instance already exists" in str(e):
        print("⚠️ Streamlit runtime instance already exists! Please run `taskkill /F /IM streamlit.exe 2>nul`")
        sys.exit(1)
    else:
        raise

# Performance monitoring utility functions
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

# Title
st.title("📋 Compliance Assistant")

# Custom CSS for blue button and sidebar behavior
st.markdown("""
<style>
.stButton > button {
    background-color: #0066cc;
    color: white;
}
/* Hide sidebar by default */
section[data-testid="stSidebar"] {
    display: none;
}
/* Show sidebar when user clicks the hamburger menu */
section[data-testid="stSidebar"][aria-expanded="true"] {
    display: block;
}
</style>
""", unsafe_allow_html=True)

# Initialize RAG system
# Create PDF if it doesn't exist
pdf_path = "data/documents/sample_IT_compliance_document.pdf"
if not os.path.exists(pdf_path):
    create_sample_pdf()

# Load RAG system
rag = SimpleRAG()

# PDF Content Dropdown
with st.expander("View sample_IT_compliance_document.pdf contents", expanded=False):
    # Read PDF content dynamically
    pdf_path = "data/documents/sample_IT_compliance_document.pdf"
    if os.path.exists(pdf_path):
        try:
            from rag_system.utils import read_pdf
            pdf_content = read_pdf(pdf_path)
            st.markdown(pdf_content)
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            st.info("PDF content could not be loaded. Please check if the file exists.")
    else:
        st.warning("PDF file not found. Please ensure the document has been created.")

# Performance metrics sidebar
with st.sidebar:
    st.header("📊 Metrics")
    st.header(f"Embedding Model:")
    st.write(f"{rag.embedding_model}")
    st.header(f"Pipeline Model:")
    st.write(f"{rag.pipeline_model}")

    # Memory usage
    memory_mb = get_memory_usage()
    st.metric("Memory Usage", f"{memory_mb:.1f} MB")

    
    # Storage size
    storage_mb = get_storage_size()
    st.metric("Storage Size", f"{storage_mb:.1f} MB")

    
    # Force reload RAG system (for debugging)
    if st.button("🔄 Reload System"):
        st.cache_resource.clear()
        st.rerun()
    

# Search interface
query = st.text_input("Enter your question:", value="How many levels is Company data classified?", placeholder="Ask about compliance policies...")

if st.button("🔍 Search", type="secondary") and query:
    # Performance tracking
    start_time = time.time()
    initial_memory = get_memory_usage()
    
    with st.spinner("Searching..."):
        # Measure embedding and search time
        search_start = time.time()
        
        # Call search with 5 results
        results = rag.search(query, 5)
        
        search_time = time.time() - search_start
        
        # Calculate performance metrics
        total_time = time.time() - start_time
        final_memory = get_memory_usage()
        memory_delta = final_memory - initial_memory
        
        
        # Show best answer first
        if results and isinstance(results[0], dict) and "answer" in results[0]:
            best_result = results[0]
            st.markdown("### 🎯 Best Answer:")
            st.success(f"**{best_result['answer']}**")
            st.markdown(f"*Confidence: {best_result['similarity']:.1%}*")
            if best_result.get("citation"):
                st.markdown(f"*Source: {best_result['citation']}*")
            st.divider()
        
        # Show all results in dropdowns
        for i, result in enumerate(results, 1):
            with st.expander(f"Result {i} - Similarity: {result.get('similarity', 0):.1%}", expanded=False):
                # Handle both string and dictionary formats
                if isinstance(result, dict):
                    # Show extracted answer if available
                    if result.get("answer"):
                        st.markdown(f"**Answer:** {result['answer']}")
                    
                    # Show citation
                    if result.get("citation"):
                        st.markdown(f"**Source:** {result['citation']}")
                    
                    # Display the full text
                    st.write(result["text"])
                else:
                    # Old string format (fallback)
                    st.write(result)
        
# Footer
st.markdown("---")
st.markdown('[🐱 GitHub Repo](https://github.com/kimnewzealand/rag-tutorial)')