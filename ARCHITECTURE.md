# RAG POC Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG POC Architecture                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Layer   │    │  Processing     │    │   Storage       │
│                 │    │    Layer        │    │    Layer        │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Text          │───▶│ • Sentence      │──▶│ • ChromaDB      │
│   Documents     │    │   Transformers  │    │   Vector Store  │
│ • Queries       │    │ • Embeddings    │    │ • Local Files   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Search        │    │   Retrieval     │    │   Output        │
│   Layer         │    │   Layer         │    │   Layer         │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
|                 ◀── |                 |    |                 |
└─────────────────┘    └─────────────────┘    │                 │
                                              └─────────────────┘
```

## Detailed Component Flow

### 1. Document Ingestion
```
┌─────────────┐    ┌─────────────┐     ┌─────────────┐
│ Raw Text    │───▶│ Sentence    │───▶│ Vector      │
│ Documents   │    │ Transformer │     │ Embeddings  │
│             │    │ (Model)     │     │             |
└─────────────┘    └─────────────┘     └─────────────┘
```





### 2. Storage & Indexing
```
┌─────────────┐    ┌─────────────┐     ┌─────────────┐
│ Vector      │───▶│ ChromaDB    │───▶│ Persistent  │
│ Embeddings  │    │ Collection  │     │ Storage     │
│             │    │             │     │ (./vector_db)│
└─────────────┘    └─────────────┘     └─────────────┘
```

### 3. Query Processing
```
┌─────────────┐    ┌─────────────┐     ┌─────────────┐
│ User Query  │───▶│ Query       │───▶│ Similarity  │
│             │    │ Embedding   │     │ Search      │
└─────────────┘    └─────────────┘     └─────────────┘
                                           │
                                           ▼
┌─────────────┐    ┌─────────────┐     ┌─────────────┐
│ Search      │◀── │ Top-K       │◀───│ Cosine      │
│ Output      │    │  Results    │     │ Distance    │
│             │    │             │     │ Calculation │
└─────────────┘    └─────────────┘     └─────────────┘
```

The **query embedding** is a vector representation of the user's query, generated on-the-fly by the sentence transformer model. ChromaDB compares this to stored document embeddings using default **cosine similarity** to find and return the most relevant document chunks. The query embedding is not saved—it's used only during the search.

ChromaDB retrieves the **top-k** most similar document chunks, where *k* is a configurable number (for example, 3). These top-k results represent the document sections that are most relevant to the user's query, ranked by their similarity score.


## Technology Stack

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                              Technology Stack                                │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ ChromaDB    │  │ Sentence    │  │ HuggingFace │  │ Streamlit   │           │
│  │ Vector DB   │  │ Transformers│  │ Transformers│  │ (Web UI)    │           │
│  │ (Local)     │  │             │  │             │  │             │           │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘           │
│                          ┌─────────────┐                                      │
│                          │ Python 3.8+ │                                      │
│                          └─────────────┘                                      │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Key Features

- ✅ **Local Processing**: All components run on your machine
- ✅ **Free Dependencies**: Uses open-source libraries with no usage costs
- ✅ **Vector Database Advantage**: Uses a vector database (ChromaDB) because traditional databases like SQL are not optimized for storing and querying large vector data. Vector databases are designed for efficient similarity search on high-dimensional embeddings, enabling fast and accurate retrieval of relevant document chunks.


## Performance Characteristics

## Performance Profile

### Model Comparison

| Version                                 | Memory Usage | Storage   |
|----------------------------------------|--------------|-----------|
| 1 Embedding model all-MiniLM-L6-v2, word chunking and d n_result =3 ,Distance Metric: Cosine Similarity     | 507.7 MB     | 32.5 MB   |
|2. Embedding model paraphrase-multilingual-mpnet-base-v2 sentence chunking and d n_result =10, pipeline model deepset/roberta-base-squad2 Distance Metric: Cosine Similarity (Current)  | 740.8 MB     | 112.7 MB  |

---

---

### Abstractions and Enhancements Over Time

The first RAG system version 1 split a pdf document into word-based chunks, used basic keyword search, and returned relevant text. It used chromaDB and sentence_transformer libraries each with default models, with utility functionality written as custom functions.

This has been iterated on as follows:

- ✅ Updated embedding model in chromadb to improve semantic understanding
- ✅ Changed from general word chunking to sentence chunking ([What is sentence chunking?](https://www.pinecone.io/learn/chunking-strategies/#sentence-chunking)) (Benefit: improves retrieval accuracy and ensures more relevant, contextually complete answers).
- ✅ Increased n_results to default value 10 (initially set at 3) for better context quality (tradeoff: increases memory usage). See [ChromaDB n_results documentation](https://docs.trychroma.com/usage-guide#querying) for details.
- ✅ Added a best answer selection using [transformers QA pipeline](https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.QuestionAnsweringPipeline) to extract the most relevant answer from retrieved chunks, rather than just returning the top-matching chunk.

---

### Current Sample Queries

| Query                                         | Answer                                 |
|-----------------------------------------------|----------------------------------------|
| how often must access reviews be performed?   | quarterly                              |
| how many levels is Company data classified?   | three                                  |
| what levels is Company data classified?       | Public, Internal, and Confidential     |


## Key Terminology and References

- **Chunking**: The process of splitting a document into smaller, semantically meaningful pieces (chunks), typically by sentence or paragraph. This improves retrieval accuracy and ensures answers are contextually relevant.

- **Collection**: A logical grouping in ChromaDB where you store your document embeddings, the original text chunks, and any associated metadata (such as section numbers or titles). Each collection acts like a table in a traditional database, but is optimized for vector search.  
  - Reference: [ChromaDB Data Model - Collections](https://docs.trychroma.com/docs/overview/data-model#collections)

- **Vector Embedding**: A high-dimensional numerical representation of a text chunk, generated by a sentence transformer model from the raw document text. This captures the meaning of the text, enabling efficient similarity search and comparison in the vector database using mathematical operations.






