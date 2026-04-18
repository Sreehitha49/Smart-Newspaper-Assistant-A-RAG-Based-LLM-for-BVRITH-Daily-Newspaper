import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
PDF_FOLDER    = os.getenv("PDF_FOLDER", "./raw_pdfs")
CHROMA_DIR    = os.getenv("CHROMA_DIR", "./chroma_db")
UPLOAD_DIR    = os.getenv("UPLOAD_DIR", "./uploads")
HISTORY_FILE  = os.getenv("HISTORY_FILE", "./chat_history.json")
COLLECTION    = "newspaper"
CHUNK_SIZE    = 500
CHUNK_OVERLAP = 100
TOP_K         = 5
MODEL         = "llama-3.3-70b-versatile"