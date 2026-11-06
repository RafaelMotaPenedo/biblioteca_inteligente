from __future__ import annotations

import os
from pathlib import Path
from flask import Flask, jsonify, render_template, request, session

from engine import answer_question, load_knowledge, search, list_characters, tokenize
from internet import lookup

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE = load_knowledge(BASE_DIR / "knowledge.json")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-antes-de-publicar")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    MAX_CONTENT_LENGTH=16 * 1024,
)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "app": "Biblioteca Inteligente"})


@app.get("/api/characters")
def characters():
    return jsonify({"characters": list_characters(KNOWLEDGE["entries"])})


@app.post("/api/ask")
def ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"error": "Digite uma pergunta para começar."}), 400
    if len(question) > 500:
        return jsonify({"error": "Sua pergunta é muito longa. Tente resumir em até 500 caracteres."}), 400

    previous_topic = session.get("previous_topic")
    answer, topic = answer_question(question, KNOWLEDGE["entries"], previous_topic)
    # Evita usar a base local quando a pergunta contém termos que ela não cobre.
    # Um nome isolado ainda é respondido localmente; perguntas detalhadas podem ir à web.
    ranked = search(question, KNOWLEDGE["entries"], limit=1)
    strong = bool(ranked and ranked[0]["_score"] >= 8)
    unsupported = bool(set(tokenize(question)) - set(tokenize(' '.join(
        str(value) for value in ranked[0].values()
    )))) if ranked else True
    needs_web = (not strong) or (unsupported and len(tokenize(question)) >= 4)
    web_result = lookup(question) if needs_web else None
    if web_result:
        answer = web_result["answer"]
        topic = "Pesquisa na internet"
    session["previous_topic"] = topic
    return jsonify({
        "question": question,
        "answer": answer,
        "topic": topic,
        "engine": "Wikipédia" if web_result else "base de conhecimento",
        "sources": web_result["sources"] if web_result else [],
    })


@app.get("/api/search")
def search_api():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": []})
    results = search(query, KNOWLEDGE["entries"], limit=6)
    return jsonify({
        "results": [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "topic": item.get("topic"),
                "type": item.get("type", "topic"),
                "summary": item.get("text", "")[:260],
            }
            for item in results
        ]
    })


@app.post("/api/reset")
def reset_context():
    session.pop("previous_topic", None)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Use 0.0.0.0 when testing on a local network; public QR codes need a deployed URL.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
