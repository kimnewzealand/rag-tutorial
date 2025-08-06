"""
Simple RAG MVP
A basic RAG system using ChromaDB and sentence transformers
"""

import chromadb
from sentence_transformers import SentenceTransformer
import PyPDF2

class SimpleRAG:
    def __init__(self):
        # Initialize ChromaDB and embedding model
        self.embedding_model = 'all-MiniLM-L6-v2'  # Store for later retrieval
        self.client = chromadb.PersistentClient(path="./data/vector_db")
        self.collection = self.client.get_or_create_collection("documents")
        self.model = SentenceTransformer(self.embedding_model)
        print("✅ RAG system ready!")
    
    def read_pdf(self, pdf_path):
        """Read text from PDF file"""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return " ".join(page.extract_text() for page in pdf_reader.pages)
    
    def chunk_text(self, text, chunk_size=200, overlap=50):
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:
                chunks.append(chunk.strip())
        
        return chunks
    
    def add_pdf(self, pdf_path):
        """Add PDF document to the system"""
        text = self.read_pdf(pdf_path)
        chunks = self.chunk_text(text)
        
        # Add to ChromaDB with auto-generated IDs
        self.collection.add(
            documents=chunks,
            ids=[f"doc_{i}" for i in range(len(chunks))]
        )
        print(f"✅ Added {len(chunks)} chunks from PDF")
    
    def search(self, query, n_results=3):
        """Search for relevant documents"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results["documents"][0]
    
    def get_model_info(self):
        """Get information about the embedding model"""
        return {
            "name": self.embedding_model,
            "dimensions": self.model.get_sentence_embedding_dimension(),
            "max_length": self.model.max_seq_length
        }