"""
Run this script once to index all PDFs and images from your raw_pdfs folder.
Usage:  python build_db.py
"""
from database import build_database

if __name__ == "__main__":
    build_database()