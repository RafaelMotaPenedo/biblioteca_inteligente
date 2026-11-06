"""Núcleo da Biblioteca Inteligente: busca lexical, ranking e contexto simples."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

STOPWORDS = {
    "a", "as", "o", "os", "um", "uma", "uns", "umas", "de", "do", "da",
    "dos", "das", "e", "ou", "em", "no", "na", "nos", "nas", "que",
    "quem", "qual", "quais", "como", "por", "para", "com", "sobre", "me",
    "diga", "explique", "é", "ele", "ela", "se", "foi", "era", "tem",
    "são", "ao", "aos", "um", "uma", "eu", "o", "a", "isso", "essa",
    "esse", "este", "esta", "dos", "das", "lhe", "mais", "muito", "muita"
}
FOLLOW_UP_MARKERS = {
    "ele", "ela", "eles", "elas", "seu", "sua", "dele", "dela",
    "tambem", "também", "e", "isso", "essa", "esse", "nesse", "nessa"
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.casefold())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("ç", "c")


def tokenize(text: str) -> list[str]:
    return [
        word for word in re.findall(r"[a-z0-9]+", normalize(text))
        if len(word) > 1 and word not in STOPWORDS
    ]


def load_knowledge(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data.get("entries"), list):
        raise ValueError("O JSON precisa conter uma lista 'entries'.")
    for index, entry in enumerate(data["entries"]):
        if not isinstance(entry, dict) or "text" not in entry:
            raise ValueError(f"Registro inválido na posição {index}.")
        entry.setdefault("id", f"entry-{index}")
        entry.setdefault("topic", entry.get("name", "Assunto sem nome"))
        entry.setdefault("name", entry["topic"])
        entry.setdefault("keywords", [])
        entry.setdefault("source", "Fonte não informada")
        entry.setdefault("characteristics", [])
        entry.setdefault("behavior", "")
        entry.setdefault("relationships", {})
        entry.setdefault("conflicts", [])
        entry.setdefault("development", {})
    return data


def _entry_search_text(entry: dict[str, Any]) -> str:
    fields = [
        entry.get("name", ""), entry.get("topic", ""), entry.get("text", ""),
        entry.get("behavior", ""), " ".join(entry.get("keywords", [])),
        " ".join(entry.get("characteristics", [])),
        " ".join(entry.get("conflicts", [])),
        " ".join(str(k) + " " + str(v) for k, v in entry.get("relationships", {}).items()),
        " ".join(str(k) + " " + str(v) for k, v in entry.get("development", {}).items())
    ]
    return " ".join(str(x) for x in fields)


def search(question: str, entries: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    """Busca simples por relevância. Não é um modelo semântico nem um LLM."""
    query_words = set(tokenize(question))
    if not query_words:
        return []

    ranked = []
    for entry in entries:
        topic_words = set(tokenize(entry.get("topic", "")))
        name_words = set(tokenize(entry.get("name", "")))
        keyword_words = set(tokenize(" ".join(entry.get("keywords", []))))
        all_words = set(tokenize(_entry_search_text(entry)))

        score = (
            7 * len(query_words & name_words)
            + 6 * len(query_words & topic_words)
            + 4 * len(query_words & keyword_words)
            + 1 * len(query_words & all_words)
        )

        # Pequeno bônus para correspondência de frase no nome ou tópico.
        normalized_q = normalize(question).strip()
        normalized_topic = normalize(entry.get("topic", ""))
        normalized_name = normalize(entry.get("name", ""))
        if normalized_q and (normalized_q in normalized_topic or normalized_q in normalized_name):
            score += 8

        if score > 0:
            ranked.append({**entry, "_score": score})

    ranked.sort(key=lambda item: (-item["_score"], item.get("topic", "")))
    return ranked[:limit]


def detect_intent(question: str) -> str:
    q = set(tokenize(question))
    if q & {"relacao", "relacoes", "amizade", "pai", "mae", "irma", "irmao", "conflito", "conflitos"}:
        return "relationships"
    if q & {"caracteristica", "caracteristicas", "personalidade", "fisica", "psicologica"}:
        return "characteristics"
    if q & {"comportamento", "comporta", "atitude", "atitudes"}:
        return "behavior"
    if q & {"mudanca", "mudancas", "evolucao", "desenvolvimento", "inicio", "meio", "final"}:
        return "development"
    if q & {"conflito", "conflitos", "problema", "problemas"}:
        return "conflicts"
    return "general"


def format_entry(entry: dict[str, Any], intent: str = "general") -> str:
    topic = entry.get("topic", "Assunto")
    lines = [f"Assunto: {topic}", ""]

    if intent == "characteristics" and entry.get("characteristics"):
        lines.append("Características: " + ", ".join(entry["characteristics"]) + ".")
        lines.append("")
    elif intent == "behavior" and entry.get("behavior"):
        lines.extend(["Comportamento:", entry["behavior"], ""])
    elif intent == "relationships" and entry.get("relationships"):
        lines.append("Relações:")
        for person, description in entry["relationships"].items():
            lines.append(f"- {person}: {description}")
        lines.append("")
    elif intent == "conflicts" and entry.get("conflicts"):
        lines.append("Conflitos:")
        for conflict in entry["conflicts"]:
            lines.append(f"- {conflict}")
        lines.append("")
    elif intent == "development" and entry.get("development"):
        lines.append("Mudanças ao longo da história:")
        for phase, description in entry["development"].items():
            lines.append(f"- {phase.capitalize()}: {description}")
        lines.append("")
    else:
        lines.extend([entry.get("text", "Não há resumo disponível."), ""])

    lines.append(f"Fonte registrada: {entry.get('source', 'Não informada')}")
    return "\n".join(lines)


def answer_question(
    question: str,
    entries: list[dict[str, Any]],
    previous_topic: str | None = None
) -> tuple[str, str | None]:
    """Retorna (resposta, tópico para memória curta)."""
    cleaned = question.strip()
    if not cleaned:
        return "Digite uma pergunta para pesquisar.", previous_topic

    q_norm = normalize(cleaned)
    if q_norm in {"oi", "ola", "bom dia", "boa tarde", "boa noite", "olá"}:
        return "Olá! Sou a Biblioteca Inteligente. Pergunte sobre personagens, relações, conflitos ou acontecimentos do livro.", previous_topic

    # Resolve perguntas curtas de acompanhamento usando o último assunto conhecido.
    tokens = set(tokenize(cleaned))
    has_followup = bool(tokens & FOLLOW_UP_MARKERS) or len(tokens) <= 3
    search_question = cleaned
    if previous_topic and has_followup:
        search_question = f"{previous_topic} {cleaned}"

    results = search(search_question, entries)
    if not results:
        return (
            "Não encontrei informação suficiente na base para responder com confiança. "
            "Tente incluir o nome do personagem ou reformular a pergunta. "
            "Também é possível ampliar knowledge.json com novas anotações.",
            previous_topic
        )

    best = results[0]
    # Evita responder com um resultado muito fraco.
    if best["_score"] < 2:
        return "Encontrei correspondências fracas, mas não o suficiente para responder com confiança. Tente reformular a pergunta.", previous_topic

    intent = detect_intent(cleaned)
    response = format_entry(best, intent)
    if len(results) > 1:
        related = [r["topic"] for r in results[1:4] if r["id"] != best["id"]]
        if related:
            response += "\n\nAssuntos relacionados: " + ", ".join(related)

    return response, best.get("topic", previous_topic)


def list_characters(entries: list[dict[str, Any]]) -> list[str]:
    return sorted(
        entry.get("name", entry.get("topic", ""))
        for entry in entries if entry.get("type") == "character"
    )
