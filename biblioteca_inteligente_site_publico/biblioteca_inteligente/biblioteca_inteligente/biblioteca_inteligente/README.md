# Biblioteca Inteligente

Projeto de estudo em Python sobre *O Menino do Pijama Listrado*.

## Requisitos
- Python 3.11 ou versão recente
- Nenhuma biblioteca externa para a versão atual
- Internet não é necessária

## Estrutura
- `main.py`: interface de terminal e comandos
- `engine.py`: normalização, busca, ranking e memória curta de contexto
- `knowledge.json`: base de conhecimento estruturada
- `tests/test_engine.py`: testes automatizados

## Executar no Windows
Abra o CMD ou PowerShell na pasta do projeto:

```bat
py -3.11 main.py
```

Se esse comando não funcionar:

```bat
python main.py
```

## Comandos
- `/ajuda`
- `/personagens`
- `/buscar kotler`
- `/fonte`
- `/limpar`
- `sair`

## Testar
Na pasta do projeto:

```bat
py -3.11 -m unittest discover -s tests -v
```

## Como adicionar informações
Abra `knowledge.json` e adicione um objeto à lista `entries`. Campos recomendados:
- `id`: identificador único
- `type`: `character` ou `topic`
- `name` e `topic`
- `characteristics`: lista de características
- `behavior`: descrição do comportamento
- `relationships`: dicionário de relações
- `conflicts`: lista de conflitos
- `development`: etapas da história
- `text`: resumo usado como resposta padrão
- `keywords`: palavras que ajudam a localizar o registro
- `source`: origem da anotação

Mantenha JSON válido: aspas duplas, vírgulas entre campos e sem vírgula sobrando no último item.

## Limitações atuais
Esta versão implementa busca lexical com pontuação e contexto curto. Não é um modelo de linguagem, não aprende automaticamente e não garante compreensão semântica profunda. As respostas são limitadas ao conteúdo da base.

Para uma versão generativa, pode-se conectar um LLM local ou uma API, mantendo a recuperação de trechos como base para respostas verificáveis.

## Nota sobre fontes
Os registros iniciais são resumos de estudo, não citações literais. Distinga o romance de sua adaptação cinematográfica e verifique detalhes na edição usada.
