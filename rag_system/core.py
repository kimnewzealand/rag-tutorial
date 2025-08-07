"""
Simple RAG MVP
A basic RAG system using ChromaDB and sentence transformers
"""

import chromadb
from sentence_transformers import SentenceTransformer
from transformers import pipeline,AutoTokenizer
import torch
import re
from .utils import read_pdf, reload_document, reset_database, add_pdf

class SimpleRAG:
    
    def __init__(self, embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2',pipeline_model='deepset/roberta-base-squad2',device=-1):
        try: 
            self.embedding_model = embedding_model
            self.pipeline_model = pipeline_model
            self.device = device
            # ChromaDB 0.3.29 uses different API
            self.client = chromadb.Client(chromadb.config.Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./data/vector_db"
            ))
            self.collection = self.client.get_or_create_collection("documents")
            
            try:
                self.model = SentenceTransformer(embedding_model)
                print(f"✅ Embedding model loaded: {embedding_model}")
            except Exception as e:
                print(f"❌ Failed to load embedding model '{embedding_model}': {e}")
                print("💡 Try using a valid model like 'sentence-transformers/all-MiniLM-L6-v2'")
                raise
            
            try:
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model=pipeline_model,
                    tokenizer=pipeline_model,
                    device=-1
                )
                print(f"✅ QA pipeline loaded: {pipeline_model}")
            except Exception as e:
                print(f"❌ Failed to load QA pipeline '{pipeline_model}': {e}")
                print("💡 Try using a valid model like 'deepset/roberta-base-squad2'")
                raise
                
            print(f"✅ RAG system ready.")
        except Exception as e:
            print(f"❌ Error initializing RAG system: {e}")
            raise
    
    def chunk_text(self, text, max_chunk_size=200):
        """Split text into chunks using Transformers tokenizer for better sentence detection"""
        
        # Use the same tokenizer as the embedding model for consistency
        tokenizer = AutoTokenizer.from_pretrained(self.embedding_model)
        
        # Split text into sentences using tokenizer
        # The tokenizer can help identify sentence boundaries more accurately
        tokens = tokenizer.tokenize(text)
        
        # Reconstruct text from tokens to get proper sentence boundaries
        reconstructed_text = tokenizer.convert_tokens_to_string(tokens)
        
        # Split by sentence endings (., !, ?) but preserve section numbers
        sentences = re.split(r'([.!?]+)', reconstructed_text)
        
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + punctuation
            
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk + full_sentence) <= max_chunk_size:
                current_chunk += full_sentence + " "
            else:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                # Start new chunk with current sentence
                current_chunk = full_sentence + " "
        
        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Filter out chunks that are too short
        chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]
        
        return chunks
    
    def search(self, query, n_results=10):
        """Search for relevant documents and extract answers with citations"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "distances", "metadatas"]
        )
        
        documents = results["documents"][0]
        distances = results["distances"][0]
        # Get the metadata for each document result; if not present, assign a default section label
        metadatas = results["metadatas"][0] if results["metadatas"] else [{"section": ""} for _ in documents]
        
        # Return documents with answer extraction and citations
        search_results = []
        for i, doc in enumerate(documents):
            # Extract potential answer from document using transformers
            answer = self._extract_answer_with_transformers(query, doc)
            
            # Extract section number and title from the document
            # Look for pattern like "1." or "1.1"
            section_match = re.search(r"\b((?:\d+\.)+\d*)\s*(.+)", doc)
            if section_match:
                section_num = section_match.group(1).rstrip('.')
                section_title = section_match.group(2).split('.')[0].strip()  # Take first sentence as title
                # Try to get document title from metadata if available
                doc_title = metadatas[i].get("document_title", "") if i < len(metadatas) and isinstance(metadatas[i], dict) else ""
                if doc_title:
                    citation = f"{doc_title}.pdf - Section {section_num}. {section_title}"
                else:
                    citation = f"Section {section_num}. {section_title}"
            else:
                # Try to get document title from metadata if available
                doc_title = metadatas[i].get("document_title", "") if i < len(metadatas) and isinstance(metadatas[i], dict) else ""
                if doc_title:
                    citation = f"{doc_title} - Section not found"
                else:
                    citation = "Issues with citation"
            
            search_results.append({
                "text": doc,
                "similarity": 1 - distances[i] if distances[i] is not None else 0,
                "answer": answer,
                "citation": citation
            })
        
        return search_results
    
    def _extract_answer_with_transformers(self, query, document):
        """Extract answer using transformers QA pipeline"""
        if self.qa_pipeline is None:
            raise Exception("QA pipeline is not available")
        
        # Use transformers QA pipeline
        result = self.qa_pipeline(
            question=query,
            context=document,
            max_answer_len=50,
            handle_impossible_answer=True
        )
        
        # Return the extracted answer
        return result['answer']
         
    
