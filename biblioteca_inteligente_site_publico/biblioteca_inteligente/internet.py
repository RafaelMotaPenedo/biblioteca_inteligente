"""Pesquisa pública na Wikipédia em português, sem chave de API."""
from __future__ import annotations
import json
import re
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

API = 'https://pt.wikipedia.org/w/api.php'
CONTEXT = 'O Menino do Pijama Listrado'


def _request(params):
    url = API + '?' + urlencode(params)
    req = Request(url, headers={'User-Agent': 'BibliotecaInteligenteEscolar/1.1 (projeto educativo; contato via aplicacao)', 'Accept': 'application/json'})
    with urlopen(req, timeout=6) as response:
        return json.load(response)


def lookup(question: str):
    """Retorna resposta com trechos e URLs; falhas de rede não derrubam o site."""
    query = re.sub(r'\s+', ' ', question).strip()[:180]
    if not query:
        return None
    # O projeto é sobre o livro; a pesquisa adiciona contexto sem prometer resposta perfeita.
    searches = [f'"{CONTEXT}" {query}', query]
    for term in searches:
        try:
            data = _request({'action': 'query', 'list': 'search', 'srsearch': term,
                             'srnamespace': 0, 'srlimit': 3, 'format': 'json', 'utf8': 1})
            hits = data.get('query', {}).get('search', [])
            if not hits:
                continue
            ids = '|'.join(str(hit['pageid']) for hit in hits)
            pages = _request({'action': 'query', 'prop': 'extracts|info', 'inprop': 'url',
                              'exintro': 1, 'explaintext': 1, 'exchars': 1300,
                              'pageids': ids, 'format': 'json', 'redirects': 1})
            collected = []
            for hit in hits:
                page = pages.get('query', {}).get('pages', {}).get(str(hit['pageid']), {})
                excerpt = re.sub(r'\s+', ' ', page.get('extract', '')).strip()
                url = page.get('fullurl', '')
                if excerpt and urlparse(url).hostname == 'pt.wikipedia.org':
                    collected.append({'title': page.get('title', hit['title']),
                                      'url': url, 'excerpt': excerpt[:850]})
            if collected:
                text = 'Encontrei estas informações na Wikipédia (trechos de páginas, não uma resposta gerada por IA):\n\n'
                text += '\n\n'.join(f"{item['title']}: {item['excerpt']}" for item in collected[:2])
                text += '\n\nConfira as fontes abaixo. Os trechos podem não responder exatamente à pergunta.'
                return {'answer': text, 'sources': [{'title': x['title'], 'url': x['url']} for x in collected[:2]]}
        except (OSError, ValueError, KeyError, TimeoutError):
            return None
    return None
