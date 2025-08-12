# Simple RAG Tutorial


A Retrieval-Augmented Generation (RAG) system combines information retrieval with language generation. It works by searching a collection of documents to find relevant content for a user's question, then uses that information to generate a helpful answer. 

In this project, the RAG system reads a PDF document, retrieves the most relevant sections based on your query, and presents the answer in a user-friendly web app.

See deployed app version here:
https://compliance-rag.streamlit.app/

I used the Cursor agent on Auto model select to help build this project.

**Benefits of automating this process include:**
- **Faster information retrieval:** Instantly find relevant content without manual searching.
- **Improved accuracy:** Reduces the risk of missing important details in large documents.
- **Consistency:** Ensures the same process is followed every time, minimizing human error.
- **Reduced Hallucination:** The RAG system only returns information that actually exists in your documents, minimizing the risk of generating made-up or inaccurate answers. This means you get reliable, document-grounded responses instead of AI "hallucinations."
- **Time savings:** Frees up time for more valuable tasks by automating repetitive lookups.
- **Scalability:** Easily handles multiple or large documents as your needs grow.
- **Checklist Tracking:** The system can help maintain a checklist of compliance tasks or requirements, marking off what has already been completed. This ensures nothing is overlooked and provides a clear record of progress.



## 🚀 Features

- **Completely Free** - No API costs or cloud services required
- **Local Processing** - Everything runs on your machine
- **Simple Setup** - Minimal dependencies and configuration
- **Persistent Storage** - Documents are saved locally

## 📋 Requirements

- Python 3.8+
- pip package manager
- virtual environment

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Create sample pdf:**
   ```bash
   python scripts/create_sample_pdf.py
   ```
3. **Run unit tests (optional):**
   ```bash
   python -m unittest tests.test_create_sample_pdf -v
   ```
4. **Run the demo app:**
   ```bash
   streamlit run rag_system/web_app.py
   ```

## 📁 Project Structure

```
rag-tutorial/
├── rag_system/
│   ├── core.py                # RAG core logic
│   ├── utils.py               # RAG utilities
│   └── web_app.py             # Streamlit web app
├── scripts/
│   └── create_sample_pdf.py   # Script to generate sample PDF for testing
├── tests/
│   └── test_create_sample_pdf.py  # Unit tests for PDF creation
├── data/
│   └── documents/             # Folder for PDF documents
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── ARCHITECTURE.md            # Project architecture
```

## 🧪 Testing

The project includes unit tests to verify that the PDF creation functionality works correctly:

- **Test PDF creation**: Verifies that the PDF file is generated successfully
- **Test content verification**: Ensures that expected content appears in the generated PDF
- **Test multiple content items**: Validates that various sections are included
- **Test page count**: Confirms the PDF has the expected number of pages

Run all tests with:
```bash
python -m unittest tests.test_create_sample_pdf -v
```

## 📚 Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [Sentence Transformers](https://www.sbert.net/)


