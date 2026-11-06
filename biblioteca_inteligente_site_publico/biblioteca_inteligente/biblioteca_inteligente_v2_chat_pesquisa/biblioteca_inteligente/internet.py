"""Busca verificável na Wikipédia em português, com tolerância a falhas."""
from __future__ import annotations
import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = 'https://pt.wikipedia.org/w/api.php'
HEADERS = {'User-Agent': 'BibliotecaInteligente/2.0 (projeto educacional; consulta informativa)', 'Accept': 'application/json'}

def _request(params):
    req = Request(API + '?' + urlencode(params), headers=HEADERS)
    with urlopen(req, timeout=5) as response:
        return json.load(response)

def lookup(question: str, context: str = ''):
    query = re.sub(r'\s+', ' ', question).strip()[:180]
    if not query:
        return None
    searches = [query]
    if context and context.casefold() not in query.casefold():
        searches.insert(0, f'{context} {query}')
    for term in searches:
        try:
            data = _request({'action': 'query', 'list': 'search', 'srsearch': term,
                             'srnamespace': 0, 'srlimit': 5, 'format': 'json'})
            hits = data.get('query', {}).get('search', [])
            if not hits:
                continue
            pages = _request({'action': 'query', 'prop': 'extracts|info', 'inprop': 'url',
                              'exintro': 1, 'explaintext': 1, 'exchars': 1200,
                              'pageids': '|'.join(str(x['pageid']) for x in hits),
                              'format': 'json', 'redirects': 1}).get('query', {}).get('pages', {})
            results = []
            for hit in hits:
                page = pages.get(str(hit['pageid']), {})
                excerpt = re.sub(r'\s+', ' ', page.get('extract', '')).strip()
                url = page.get('fullurl', '')
                if excerpt and url.startswith('https://pt.wikipedia.org/wiki/'):
                    results.append({'title': page.get('title', hit['title']), 'url': url, 'excerpt': excerpt[:700]})
                if len(results) == 3:
                    break
            if results:
                return {'answer': 'Resultados encontrados na Wikipédia (resumos de fontes, não uma resposta escrita por IA):\n\n' + '\n\n'.join(f"{r['title']}: {r['excerpt']}" for r in results) + '\n\nConfira os links abaixo para verificar as informações.', 'sources': [{'title': r['title'], 'url': r['url']} for r in results]}
        except (OSError, ValueError, KeyError, TimeoutError):
            return None
    return None
