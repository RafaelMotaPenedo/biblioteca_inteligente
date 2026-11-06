"""Interface de terminal da Biblioteca Inteligente."""
from pathlib import Path
import sys

from engine import answer_question, list_characters, load_knowledge, search

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_PATH = BASE_DIR / "knowledge.json"


def show_help():
    print("""
Comandos disponíveis:
  /ajuda                 Mostra esta ajuda
  /personagens           Lista personagens cadastrados
  /buscar <termo>        Mostra resultados de busca
  /fonte                 Explica como as fontes são registradas
  /limpar                Limpa a memória curta da conversa
  sair                   Encerra o programa

Você também pode perguntar normalmente, por exemplo:
  Quem é Bruno?
  Quais são as características de Kotler?
  Como é a relação entre Bruno e Shmuel?
  Como o pai de Bruno muda durante a história?
""")


def main():
    try:
        data = load_knowledge(KNOWLEDGE_PATH)
    except FileNotFoundError:
        print(f"Erro: não encontrei {KNOWLEDGE_PATH.name}.")
        print("Deixe knowledge.json na mesma pasta de main.py.")
        return 1
    except (ValueError, OSError) as exc:
        print(f"Não foi possível carregar a base: {exc}")
        return 1

    entries = data["entries"]
    previous_topic = None

    print("=" * 64)
    print("                 BIBLIOTECA INTELIGENTE")
    print("=" * 64)
    print(f"Livro inicial: {data.get('book', 'Não definido')}")
    print(f"Registros carregados: {len(entries)}")
    print("Digite /ajuda para ver os comandos ou 'sair' para encerrar.")
    print("Observação: as respostas vêm da base local; não é um LLM.\n")

    while True:
        try:
            question = input("Você > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando. Até a próxima!")
            return 0

        if not question:
            continue

        normalized = question.casefold().strip()
        if normalized in {"sair", "exit", "quit"}:
            print("Biblioteca encerrada.")
            return 0

        if normalized == "/ajuda":
            show_help()
            continue

        if normalized == "/personagens":
            print("Personagens cadastrados:")
            for name in list_characters(entries):
                print(f"  - {name}")
            print()
            continue

        if normalized == "/fonte":
            print("Cada registro tem o campo 'source'. Nesta versão, são resumos e anotações")
            print("de estudo; não são citações literais. Verifique detalhes na edição do livro.")
            print("O romance e a adaptação cinematográfica podem divergir.\n")
            continue

        if normalized == "/limpar":
            previous_topic = None
            print("Memória curta da conversa limpa.\n")
            continue

        if normalized.startswith("/buscar "):
            term = question[len("/buscar "):].strip()
            results = search(term, entries)
            if not results:
                print("Nenhum resultado encontrado.\n")
            else:
                for result in results:
                    print(f"- {result['topic']} (relevância {result['_score']})")
                    print(f"  {result['text'][:240]}")
            print()
            continue

        if normalized.startswith("/"):
            print("Comando desconhecido. Digite /ajuda.\n")
            continue

        response, previous_topic = answer_question(question, entries, previous_topic)
        print(f"\nBiblioteca > {response}\n")


if __name__ == "__main__":
    sys.exit(main())
