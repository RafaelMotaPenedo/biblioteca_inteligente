# Atualizar o site que já está no Render

1. Extraia este ZIP. Entre na pasta `biblioteca_inteligente`.
2. No GitHub, abra o repositório `RafaelMotaPenedo/biblioteca_inteligente`.
3. **Importante:** envie os arquivos para a MESMA pasta que o Render usa como **Root Directory**. Se o Render mostra `biblioteca_inteligente_site_publico`, abra essa pasta no GitHub antes de enviar, ou atualize o Root Directory conforme o caminho real.
4. Substitua `app.py`, `internet.py`, `templates/index.html`, `static/js/app.js`, `static/css/style.css` e mantenha `engine.py`, `knowledge.json` e `requirements.txt`.
5. Faça o commit. O Render deve iniciar novo deploy automaticamente. Se não iniciar, use **Manual Deploy → Deploy latest commit**.
6. Confira **Build Command:** `pip install -r requirements.txt` e **Start Command:** `gunicorn app:app`.
7. Aguarde o status **Live** e teste no seu endereço atual.

## O que mudou
- Modo automático, somente biblioteca ou Wikipédia.
- Histórico de até 20 perguntas e respostas **na aba atual**; limpar conversa.
- Continuidade básica para perguntas curtas usando o tópico anterior (sessão Flask).
- Links verificáveis quando a busca na Wikipédia encontra resultados.
- Sem chave de API nem cobranças por modelo de IA.

## Limitações honestas
- A Wikipédia não cobre todas as perguntas sobre o livro; o resultado pode ser apenas um resumo de uma página relacionada.
- Não é um chatbot com modelo de linguagem: não gera sínteses inéditas nem compreende todas as referências de contexto.
- O histórico desaparece ao recarregar a página; não é salvo em contas ou banco de dados.
- Se a rede estiver indisponível, a busca online pode falhar e a base local continua acessível.
- A hospedagem gratuita do Render pode entrar em repouso após inatividade.
