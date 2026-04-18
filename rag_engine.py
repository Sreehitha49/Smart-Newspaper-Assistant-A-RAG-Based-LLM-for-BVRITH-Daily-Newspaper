import os
from groq import Groq
from config import GROQ_API_KEY, MODEL, TOP_K, UPLOAD_DIR
from helpers import extract_text, extract_text_from_image, chunk_text
from database import get_collection, get_embedder

groq_client = Groq(api_key=GROQ_API_KEY)


def correct_query(query):
    """Auto-correct spelling and grammar in user query before searching"""
    r = groq_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content":
             "You are a spelling and grammar corrector. "
             "Correct any spelling mistakes or grammar errors in the user's query. "
             "Return ONLY the corrected query, nothing else. "
             "Do not change the meaning. If query is already correct, return it as is."},
            {"role": "user", "content": query}
        ],
        temperature=0.0,
        max_tokens=100
    )
    return r.choices[0].message.content.strip()


def retrieve(query):
    col      = get_collection()
    embedder = get_embedder()

    corrected = correct_query(query)
    print(f"Original : {query}")
    print(f"Corrected: {corrected}")

    emb = embedder.encode(corrected).tolist()
    res = col.query(
        query_embeddings=emb,
        n_results=TOP_K,
        include=["documents", "metadatas"]
    )
    parts, sources = [], set()
    for chunk, m in zip(res["documents"][0], res["metadatas"][0]):
        parts.append(f"[From: {m['source']}]\n{chunk}")
        sources.add(m["source"])
    return "\n\n--\n\n".join(parts), list(sources), corrected


def ask(question, context, history=None, corrected_query=None):
    sys_prompt = (
        "You are a Smart Newspaper Assistant with memory of the entire conversation.\n"
        "Answer ONLY from the provided newspaper context.\n"
        "If the answer is not in the context say: "
        "'I couldn't find that in the uploaded newspapers.'\n"
        "IMPORTANT: You remember everything discussed in this conversation.\n"
        "When the user asks follow-up questions like 'tell me more', 'explain that', "
        "'what about...' — always refer back to previous messages to understand what they mean.\n"
        "Be clear, friendly, detailed and concise. Mention the source edition when relevant."
    )
    messages = [{"role": "system", "content": sys_prompt}]

    if history:
        messages += history

    user_content = f"Context:\n{context}\n\nQuestion: {question}"
    if corrected_query and corrected_query.lower() != question.lower():
        user_content = (
            f"Context:\n{context}\n\n"
            f"[Note: User wrote '{question}', interpreted as '{corrected_query}']\n"
            f"Question: {corrected_query}"
        )

    messages.append({"role": "user", "content": user_content})

    r = groq_client.chat.completions.create(
        model=MODEL, messages=messages,
        temperature=0.3, max_tokens=1024
    )
    return r.choices[0].message.content


def summarize(pdf_name):
    col = get_collection()
    r   = col.get(where={"source": pdf_name}, include=["documents"])
    if not r["documents"]:
        return f"No data found for {pdf_name}."
    text = "\n".join(r["documents"][0])
    r2 = groq_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": "Summarize this newspaper edition. "
                        "Use bullet points for key topics, events, and highlights."},
            {"role": "user", "content": text}
        ],
        temperature=0.3, max_tokens=800
    )
    return r2.choices[0].message.content


def add_file(path):
    col      = get_collection()
    embedder = get_embedder()

    name = os.path.basename(path)
    ext  = name.lower().split('.')[-1]

    if ext == 'pdf':
        text  = extract_text(path)
        ftype = 'pdf'
    elif ext in ['jpg', 'jpeg', 'png', 'webp']:
        text  = extract_text_from_image(path)
        ftype = 'image'
    else:
        return 0

    chunks = chunk_text(text)
    ids_   = [f"{name}__chunk_{i}" for i in range(len(chunks))]
    metas_ = [{"source": name, "chunk_index": i, "type": ftype}
              for i in range(len(chunks))]
    emb    = embedder.encode(chunks).tolist()
    col.add(documents=chunks, embeddings=emb, ids=ids_, metadatas=metas_)
    return len(chunks)