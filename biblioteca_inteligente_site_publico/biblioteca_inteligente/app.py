from __future__ import annotations
import os
from pathlib import Path
from flask import Flask, jsonify, render_template, request, session
from engine import answer_question, load_knowledge, search, list_characters, tokenize, normalize
from internet import lookup

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE = load_knowledge(BASE_DIR / 'knowledge.json')
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', MAX_CONTENT_LENGTH=16 * 1024)

@app.get('/')
def index():
    return render_template('index.html')

@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'app': 'Biblioteca Inteligente'})

@app.get('/api/characters')
def characters():
    return jsonify({'characters': list_characters(KNOWLEDGE['entries'])})

def _is_followup(question):
    words = set(tokenize(question))
    q = normalize(question).strip()
    return (len(words) <= 5 and any(q.startswith(prefix) for prefix in ('e ', 'mas ', 'por que ', 'por quê ', 'como ele', 'como ela', 'e ele', 'e ela', 'e depois', 'o que aconteceu depois', 'fale mais', 'explique melhor', 'qual foi'))) or bool(words & {'dele', 'dela', 'disso', 'nisso'})

@app.post('/api/ask')
def ask():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({'error': 'Envie uma pergunta válida.'}), 400
    question = str(payload.get('question', '')).strip()
    if not question:
        return jsonify({'error': 'Digite uma pergunta para começar.'}), 400
    if len(question) > 500:
        return jsonify({'error': 'Limite de 500 caracteres por pergunta.'}), 400
    mode = payload.get('mode', 'auto')
    if mode not in ('auto', 'local', 'web'):
        return jsonify({'error': 'Modo de pesquisa inválido.'}), 400
    previous_topic = session.get('previous_topic')
    previous_question = session.get('previous_question', '')
    contextual = f'{previous_topic}: {question}' if previous_topic and _is_followup(question) else question
    answer, topic = answer_question(contextual, KNOWLEDGE['entries'], previous_topic)
    ranked = search(contextual, KNOWLEDGE['entries'], limit=1)
    strong = bool(ranked and ranked[0]['_score'] >= 8)
    # Uma pergunta sobre o livro pode ser específica mesmo contendo um personagem conhecido.
    query_words = set(tokenize(contextual))
    indexed_words = set(tokenize(str(ranked[0]))) if ranked else set()
    detailed = len(query_words) >= 4 and len(query_words - indexed_words) >= 2
    needs_web = mode == 'web' or (mode == 'auto' and (not strong or detailed))
    web_result = lookup(question, previous_topic if _is_followup(question) else '') if needs_web else None
    if web_result:
        answer, topic = web_result['answer'], 'Pesquisa na internet'
    elif mode == 'web':
        answer = 'Não encontrei resultados verificáveis na Wikipédia agora. Tente outra formulação ou escolha o modo Automático.'
        topic = 'Pesquisa na internet'
    session['previous_topic'] = previous_topic if topic == 'Pesquisa na internet' and previous_topic else topic
    session['previous_question'] = question
    return jsonify({'question': question, 'answer': answer, 'topic': topic,
                    'engine': 'Wikipédia' if web_result else ('sem resultados online' if mode == 'web' else 'base de conhecimento'),
                    'sources': web_result['sources'] if web_result else [],
                    'followup': bool(previous_question and _is_followup(question))})

@app.get('/api/search')
def search_api():
    query = request.args.get('q', '').strip()[:500]
    results = search(query, KNOWLEDGE['entries'], limit=6) if query else []
    return jsonify({'results': [{'id': x.get('id'), 'name': x.get('name'), 'topic': x.get('topic'),
                                'type': x.get('type', 'topic'), 'summary': x.get('text', '')[:260]} for x in results]})

@app.post('/api/reset')
def reset_context():
    session.pop('previous_topic', None)
    session.pop('previous_question', None)
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')), debug=False)
