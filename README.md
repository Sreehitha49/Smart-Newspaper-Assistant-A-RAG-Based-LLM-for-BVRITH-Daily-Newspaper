# Smart Newspaper Assistant 📰

A RAG-powered (Retrieval-Augmented Generation) chatbot that lets you query your newspaper PDFs and images using natural language. Built with ChromaDB, Sentence Transformers, Groq LLM, and Flask.

---

## Features

- 🔍 Semantic search over uploaded newspaper PDFs and images
- 🧠 Query auto-correction using Groq LLM
- 📋 Edition summarization
- 🎙 Voice input (Chrome only)
- 📤 Upload PDFs/images at runtime
- 💬 Persistent chat history
- 🌙 Dark-themed responsive UI

---

## Project Structure

```
newspaper-llm-rag/
├── app.py            # Flask server + API routes
├── rag_engine.py     # Retrieval, query correction, answer generation
├── database.py       # ChromaDB setup and embedding model
├── helpers.py        # PDF/image text extraction and chunking
├── config.py         # Configuration (reads from .env)
├── build_db.py       # One-time script to index all PDFs
├── static/
│   └── index.html    # Frontend UI
├── raw_pdfs/         # Place your newspaper PDFs/images here
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd newspaper-llm-rag
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (for scanned PDFs)

- **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
- **macOS:** `brew install tesseract`
- **Windows:** Download from https://github.com/tesseract-ocr/tesseract

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get your free Groq API key at: https://console.groq.com

### 4. Add your PDFs

Place your newspaper PDF files (or images) in the `raw_pdfs/` folder:

```
raw_pdfs/
├── edition_jan_2024.pdf
├── edition_feb_2024.pdf
└── ...
```

### 5. Build the vector database

```bash
python build_db.py
```

### 6. Start the server

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## API Endpoints

| Method | Endpoint              | Description                       |
|--------|-----------------------|-----------------------------------|
| GET    | `/api/health`         | Server status + chunk count       |
| GET    | `/api/editions`       | List all indexed editions         |
| POST   | `/api/query`          | Ask a question                    |
| POST   | `/api/summarize`      | Summarize a specific edition      |
| POST   | `/api/upload`         | Upload a new PDF or image         |
| POST   | `/api/clear_session`  | Clear conversation session        |
| GET    | `/api/history`        | Get persistent chat history       |
| POST   | `/api/history/clear`  | Clear persistent chat history     |

---

## Tech Stack

- **LLM:** Groq (`llama-3.3-70b-versatile`)
- **Embeddings:** `all-MiniLM-L6-v2` (Sentence Transformers)
- **Vector DB:** ChromaDB (persistent)
- **OCR:** Tesseract + PyMuPDF
- **Backend:** Flask + Flask-CORS
- **Frontend:** Vanilla HTML/CSS/JS (dark theme)