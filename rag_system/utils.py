"""
Utility functions for the RAG system
"""

import PyPDF2
import os


def read_pdf(pdf_path):
    """
    Read text from PDF file
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error reading the PDF
    """
    # Check if file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = " ".join(page.extract_text() for page in pdf_reader.pages)
            return text
    except Exception as e:
        raise Exception(f"Error reading PDF {pdf_path}: {str(e)}")


def reset_database(rag_instance):
    """
    Clear the database and reinitialize
    
    Args:
        rag_instance: SimpleRAG instance
        
    Returns:
        None
        
    Raises:
        Exception: If there's an error resetting the database
    """
    try:
        rag_instance.client.delete_collection("documents")
        print("🗑️  Deleted old collection in chromaDB")
    except:
        pass
    
    rag_instance.collection = rag_instance.client.create_collection("documents")
    print("🔄 Created latest collection in chromaDB")


def add_pdf(rag_instance, pdf_path):
    """
    Add PDF document to the system
    
    Args:
        rag_instance: SimpleRAG instance
        pdf_path (str): Path to the PDF file
        
    Returns:
        None
        
    Raises:
        Exception: If there's an error adding the PDF
    """
    try:
        text = read_pdf(pdf_path)
        chunks = rag_instance.chunk_text(text)
        
        # Extract document title from filename
        document_title = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Create metadata for each chunk
        chunk_metadata = []
        for i, chunk in enumerate(chunks):
            chunk_metadata.append({
                "chunk_id": i,
                "document_title": document_title
            })
        
        rag_instance.collection.add(
            documents=chunks,
            ids=[f"doc_{i}" for i in range(len(chunks))],
            metadatas=chunk_metadata
        )
        print(f"✅ Added {len(chunks)} chunks from PDF")
    except Exception as e:
        raise Exception(f"Error adding PDF {pdf_path}: {str(e)}")


def reload_document(rag_instance, pdf_path):
    """
    Reload document with proper section metadata
    
    Args:
        rag_instance: SimpleRAG instance
        pdf_path (str): Path to the PDF file
        
    Returns:
        None
        
    Raises:
        Exception: If there's an error reloading the document
    """
    try:
        # Reset the database
        reset_database(rag_instance)
        
        # Add the PDF with new chunking strategy
        add_pdf(rag_instance, pdf_path)
        
        print("✅ Document reloaded with section metadata")
    except Exception as e:
        raise Exception(f"Error reloading document {pdf_path}: {str(e)}")

