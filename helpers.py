import fitz
import re
import os
from PIL import Image
import pytesseract
from config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text(path):
    """Extract text from PDF — handles both text-based and scanned image PDFs"""
    doc = fitz.open(path)
    text = ""
    for i, page in enumerate(doc):
        page_text = page.get_text()
        # If no text found, it's a scanned image — use OCR
        if not page_text.strip():
            pix      = page.get_pixmap(dpi=300)
            img_path = os.path.join(os.environ.get("TEMP", "."), f"page_{i}.png")
            pix.save(img_path)
            page_text = pytesseract.image_to_string(
                Image.open(img_path), lang='eng'
            )
            os.remove(img_path)
        text += f"\n[Page {i+1}]\n{page_text}"
    doc.close()
    return re.sub(r'\n{3,}', '\n\n', re.sub(r' {2,}', ' ', text)).strip()


def extract_text_from_image(path):
    """Extract text from image files using OCR"""
    try:
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        text = pytesseract.image_to_string(img, lang='eng')
        if not text.strip():
            return "No readable text found in this image."
        return text.strip()
    except Exception as e:
        return f"Could not extract text from image: {str(e)}"


def chunk_text(text):
    chunks, start = [], 0
    while start < len(text):
        c = text[start:start + CHUNK_SIZE]
        if c.strip():
            chunks.append(c.strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def load_all_files(folder):
    """Load both PDFs and images from folder"""
    all_docs, all_ids, all_meta = [], [], []

    pdf_files   = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]
    image_files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

    print(f"Found {len(pdf_files)} PDFs and {len(image_files)} images")

    for f in pdf_files:
        chunks = chunk_text(extract_text(os.path.join(folder, f)))
        for i, c in enumerate(chunks):
            all_docs.append(c)
            all_ids.append(f"{f}__chunk_{i}")
            all_meta.append({"source": f, "chunk_index": i, "type": "pdf"})
        print(f"  PDF: {f} → {len(chunks)} chunks")

    for f in image_files:
        chunks = chunk_text(extract_text_from_image(os.path.join(folder, f)))
        for i, c in enumerate(chunks):
            all_docs.append(c)
            all_ids.append(f"{f}__chunk_{i}")
            all_meta.append({"source": f, "chunk_index": i, "type": "image"})
        print(f"  Image: {f} → {len(chunks)} chunks")

    print(f"Total: {len(all_docs)} chunks")
    return all_docs, all_ids, all_meta