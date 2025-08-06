"""
Simple RAG MVP
A basic RAG system using ChromaDB and sentence transformers
"""

import chromadb
from sentence_transformers import SentenceTransformer
import PyPDF2
from transformers import pipeline
import torch

class SimpleRAG:
    def __init__(self, embedding_model='paraphrase-multilingual-MiniLM-L12-v2'):
        self.embedding_model = embedding_model
        self.client = chromadb.PersistentClient(path="./data/vector_db")
        self.collection = self.client.get_or_create_collection("documents")
        self.model = SentenceTransformer(embedding_model)
        
        # Initialize transformers QA pipeline
        try:
            self.qa_pipeline = pipeline(
                "question-answering",
                model="deepset/roberta-base-squad2",
                tokenizer="deepset/roberta-base-squad2",
                device=0 if torch.cuda.is_available() else -1
            )
            print("✅ QA pipeline loaded successfully")
        except Exception as e:
            print(f"⚠️ QA pipeline not available: {e}")
            self.qa_pipeline = None
        
        print(f"✅ RAG system ready with {embedding_model}")
    
    def reset_database(self):
        """Clear the database and reinitialize"""
        try:
            self.client.delete_collection("documents")
            print("🗑️ Deleted old collection")
        except:
            pass
        
        self.collection = self.client.create_collection("documents")
        print("🔄 Created new collection")
    
    def reload_document(self, pdf_path):
        """Reload document with proper section metadata"""
        self.reset_database()
        self.add_pdf(pdf_path)
        print("✅ Document reloaded with section metadata")
    
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
        """Add PDF document to the system with section tracking"""
        text = self.read_pdf(pdf_path)
        chunks = self.chunk_text(text)
        
        # Extract section information for each chunk
        chunk_metadata = []
        for i, chunk in enumerate(chunks):
            section = self._extract_section(chunk)
            chunk_metadata.append({
                "section": section,
                "chunk_id": i
            })
        
        self.collection.add(
            documents=chunks,
            ids=[f"doc_{i}" for i in range(len(chunks))],
            metadatas=chunk_metadata
        )
        print(f"✅ Added {len(chunks)} chunks from PDF")
    
    def _extract_section(self, text):
        """Extract section number from text"""
        import re
        # Look for section patterns like "1.1", "2.3", etc.
        section_match = re.search(r'(\d+\.\d+)', text)
        if section_match:
            return f"IT Compliance Agreement for using AI Section {section_match.group(1)}"
        
        # Look for main section patterns like "1.", "2.", etc.
        main_section_match = re.search(r'^(\d+)\.', text)
        if main_section_match:
            return f"IT Compliance Agreement for using AI Section {main_section_match.group(1)}"
        
        return "IT Compliance Agreement for using AI"
    
    def search(self, query, n_results=10):
        """Search for relevant documents and extract answers with citations"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "distances", "metadatas"]
        )
        
        documents = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0] if results["metadatas"] else [{"section": "Unknown Section"} for _ in documents]
        
        # Return documents with answer extraction and citations
        search_results = []
        for i, doc in enumerate(documents):
            # Extract potential answer from document using transformers
            answer = self._extract_answer_with_transformers(query, doc)
            
            # Get section citation
            section = metadatas[i].get("section", "Unknown Section") if metadatas[i] else "Unknown Section"
            
            search_results.append({
                "text": doc,
                "similarity": 1 - distances[i] if distances[i] is not None else 0,
                "answer": answer,
                "citation": section
            })
        
        return search_results
    
    def _extract_answer_with_transformers(self, query, document):
        """Extract answer using transformers QA pipeline"""
        if self.qa_pipeline is None:
            return self._extract_answer_fallback(query, document)
        
        try:
            # Use transformers QA pipeline
            result = self.qa_pipeline(
                question=query,
                context=document,
                max_answer_len=50,
                handle_impossible_answer=True
            )
            
            # Return the extracted answer
            if result['score'] > 0.3:  # Confidence threshold
                return result['answer']
            else:
                return self._extract_answer_fallback(query, document)
                
        except Exception as e:
            print(f"⚠️ Transformers QA failed: {e}")
            return self._extract_answer_fallback(query, document)
    
    def _extract_answer_fallback(self, query, document):
        """Fallback answer extraction using regex patterns"""
        query_lower = query.lower()
        doc_lower = document.lower()
        
        # Handle specific question types
        if "how many" in query_lower:
            import re
            numbers = re.findall(r'\b(?:three|four|five|six|seven|eight|nine|ten|\d+)\b', doc_lower)
            if numbers:
                return numbers[0]
        
        if "how often" in query_lower or "frequency" in query_lower:
            frequency_terms = [
                "quarterly", "monthly", "weekly", "daily", "annually", "yearly",
                "every quarter", "every month", "every week", "every day", "every year"
            ]
            for term in frequency_terms:
                if term in doc_lower:
                    return term
        
        # Default: return first meaningful sentence
        sentences = document.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:
                return sentence
        
        return document[:100]