# Biblioteca Inteligente — versão web

Uma aplicação web responsiva para explorar personagens, relações, conflitos e temas de *O Menino do Pijama Listrado*. A interface foi pensada primeiro para celular e para acesso por QR Code.

## O que esta versão inclui

- Interface web adaptável a celulares, tablets e computadores.
- Campo de pesquisa e sugestões de perguntas.
- Respostas servidas pelo motor de busca já existente no projeto.
- Memória curta por sessão para perguntas de acompanhamento.
- Rotas JSON (`/api/ask`, `/api/search`, `/api/characters`) e verificação de saúde (`/health`).
- Sem cadastro de visitantes.
- Testes do motor de busca mantidos.

## Executar localmente no Windows

Instale Python 3.11 ou mais recente. No CMD ou PowerShell, entre na pasta do projeto e rode:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py app.py
```

Abra `http://127.0.0.1:5000` no navegador do computador.

## Testar em outro celular na mesma rede Wi-Fi

1. Descubra o endereço IP local do computador com `ipconfig`.
2. No celular conectado à mesma rede Wi-Fi, abra `http://IP-DO-COMPUTADOR:5000` (substitua pelo IPv4 real).
3. Se não abrir, confira o firewall do Windows. Não exponha a porta diretamente à internet.

O endereço `127.0.0.1` só funciona no próprio dispositivo. Um QR Code impresso para várias pessoas precisa apontar para um endereço público estável.

## Como disponibilizar por QR Code

Para que pessoas fora da sua rede acessem, publique a aplicação em um serviço de hospedagem que execute Python/Flask. Um fluxo possível é:

1. Coloque a pasta do projeto em um repositório Git privado ou público, conforme sua preferência.
2. Crie um serviço web Python em uma plataforma de hospedagem que aceite Flask.
3. Configure o comando de inicialização como `gunicorn app:app` (adicione `gunicorn` ao `requirements.txt` se a plataforma Linux exigir).
4. Defina uma variável de ambiente `SECRET_KEY` com um valor aleatório e privado.
5. Depois de publicar, teste a URL pública no celular usando dados móveis, não apenas o Wi-Fi local.
6. Gere o QR Code com a URL pública final e teste-o em mais de um celular antes de imprimir.

A disponibilidade, os planos gratuitos e os comandos exigidos dependem da plataforma escolhida. Não imprima o QR Code antes de confirmar que a URL pública está funcionando.

## Segurança e limites

- O servidor limita perguntas a 500 caracteres e requisições a 16 KB.
- A chave de sessão de exemplo deve ser substituída antes da publicação.
- Não há login nem dados pessoais necessários para usar a aplicação.
- O motor atual usa busca lexical com pontuação e uma base de anotações; não é um LLM e pode errar ou não encontrar respostas.
- O conteúdo é um resumo de estudo, não substitui a leitura nem a conferência da edição usada na escola.
- Para respostas de produção, vale revisar as anotações e incluir fontes verificáveis para cada registro.

## Arquivos principais

- `app.py`: servidor Flask e API.
- `templates/index.html`: estrutura da página.
- `static/css/style.css`: estilo responsivo.
- `static/js/app.js`: envio de perguntas e interação.
- `engine.py`: motor de busca.
- `knowledge.json`: base de conhecimento.
- `main.py`: interface de terminal original.
- `tests/`: testes automatizados.

## Testes

```bat
py -m unittest discover -s tests -v
```

## Busca na internet (nova versão)

A rota `/api/ask` consulta primeiro `knowledge.json`. Quando a pergunta parece não
estar suficientemente coberta, pesquisa a API pública da Wikipédia em português.
Não precisa de chave, cadastro nem pacote adicional. O navegador recebe os links
das fontes, que aparecem abaixo da resposta. Se a internet estiver indisponível,
o site continua funcionando com a base local. A Wikipédia não cobre todas as
perguntas e seus trechos não equivalem a uma resposta produzida por IA.

Para atualizar a instalação no Windows, descompacte esta versão em uma nova pasta,
instale as dependências com `py -m pip install -r requirements.txt` e inicie
com `py app.py`. É necessário acesso à internet no computador que roda Flask.
