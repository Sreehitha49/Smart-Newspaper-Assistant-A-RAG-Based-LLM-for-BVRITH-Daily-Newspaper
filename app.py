import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from config import UPLOAD_DIR, HISTORY_FILE
from rag_engine import retrieve, ask, summarize, add_file
from database import get_collection

app = Flask(__name__, static_folder="static")
CORS(app)

os.makedirs(UPLOAD_DIR, exist_ok=True)

sessions = {}


# ── Persistent history helpers ────────────────────────────────

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


persistent_history = load_history()
print(f"Loaded {len(persistent_history)} history items ✓")


# ── Routes ────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/health")
def health():
    col = get_collection()
    return jsonify({"status": "ok", "docs_in_db": col.count()})


@app.route("/api/editions")
def editions():
    col      = get_collection()
    all_meta = col.get(include=["metadatas"])
    srcs     = sorted({m["source"] for m in all_meta["metadatas"]})
    return jsonify({"editions": srcs, "total_chunks": col.count()})


@app.route("/api/query", methods=["POST"])
def query():
    global persistent_history
    d   = request.json
    q   = d.get("question", "").strip()
    sid = d.get("session_id", "default")
    if not q:
        return jsonify({"error": "empty"}), 400

    sessions.setdefault(sid, [])
    ctx, srcs, corrected = retrieve(q)
    ans = ask(q, ctx, sessions[sid], corrected)

    sessions[sid] += [
        {"role": "user",      "content": corrected},
        {"role": "assistant", "content": ans}
    ]

    # Save to persistent history
    persistent_history.append({
        "q":         q,
        "corrected": corrected,
        "answer":    ans,
        "sources":   srcs,
        "time":      datetime.now().strftime("%d %b %Y, %I:%M %p")
    })
    save_history(persistent_history)

    return jsonify({
        "answer":    ans,
        "sources":   srcs,
        "corrected": corrected
    })


@app.route("/api/summarize", methods=["POST"])
def do_summarize():
    name = request.json.get("pdf_name", "")
    if not name:
        return jsonify({"error": "no pdf_name"}), 400
    return jsonify({"summary": summarize(name), "pdf_name": name})


@app.route("/api/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "no file"}), 400
    allowed = ('.pdf', '.jpg', '.jpeg', '.png', '.webp')
    if not f.filename.lower().endswith(allowed):
        return jsonify({"error": "PDF or image only (jpg, png, webp)"}), 400
    path = os.path.join(UPLOAD_DIR, f.filename)
    f.save(path)
    n = add_file(path)
    col = get_collection()
    return jsonify({
        "message":     f"Added {f.filename}",
        "chunks_added": n,
        "total_in_db":  col.count()
    })


@app.route("/api/clear_session", methods=["POST"])
def clear():
    sid = request.json.get("session_id", "default")
    sessions[sid] = []
    return jsonify({"ok": True})


@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify({"history": persistent_history})


@app.route("/api/history/clear", methods=["POST"])
def clear_persistent_history():
    global persistent_history
    persistent_history = []
    save_history(persistent_history)
    return jsonify({"ok": True})


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)