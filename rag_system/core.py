"""
Simple RAG MVP
A basic RAG system using ChromaDB and sentence transformers
"""

import chromadb
from transformers import pipeline,AutoTokenizer
import re
from .utils import read_pdf, reset_database, add_pdf

class SimpleRAG:
    
    def __init__(self, embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2',pipeline_model='deepset/roberta-base-squad2',device=-1):
        try: 
            self.embedding_model = embedding_model
            self.pipeline_model = pipeline_model
            # ChromaDB 0.3.29 uses different API to current version but this config is compatabile with deployed Streamlit
            self.client = chromadb.Client(chromadb.config.Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./data/vector_db"
            ))
            self.collection = self.client.get_or_create_collection("documents")
            
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
        """Split text into sentence chunks. Currently a custom utility, could be replaced with another library that handles sentence splitting."""
        
        # Use the same embedding model as the document embedding
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
        
        chunk = ""
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + punctuation
            if len(chunk + full_sentence) <= max_chunk_size:
                chunk += full_sentence + " "
            else:
                if chunk.strip():
                    chunks.append(chunk.strip())
                chunk = full_sentence + " "
        if chunk.strip():
            chunks.append(chunk.strip())
        chunks = [c for c in chunks if len(c.strip()) > 50]
        return chunks
    
    def search(self, query, n_results=5):
        """Search for relevant documents and extract answers with citations"""
        # Query the ChromaDB collection for the 5 most relevant document chunks to the input query withdistances (similarity scores), and metadata.
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "distances", "metadatas"]
        )
        
        documents = results["documents"][0]
        distances = results["distances"][0]
        # Get the metadata for each document result; if not present, assign a default section label
        metadatas = results["metadatas"][0] if results["metadatas"] else [{"section": ""} for _ in documents]
        
        # For each retrieved document, extract a specific answer and citation
        search_results = []
        for i, doc in enumerate(documents):
            # Extract potential answer from document using transformers
            answer = self._extract_answer_with_transformers(query, doc)
            
            # Custom extraction section number and title from the document. This could be replaced with a more robust solution
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
            # Assemble the search results
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
         
    
