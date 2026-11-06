# Publicar a Biblioteca Inteligente na internet

Este projeto já está configurado para hospedagem no Render, com `render.yaml`.
O site continuará funcionando sem seu notebook ligado, desde que o serviço de hospedagem esteja disponível.

## Passo a passo

1. Crie uma conta no GitHub (https://github.com/) e um repositório para o projeto.
2. Envie **os arquivos de dentro da pasta `biblioteca_inteligente`** para a raiz do repositório, incluindo `render.yaml`. Não envie `.venv`, senhas ou arquivos `.env`.
3. Acesse https://dashboard.render.com/ e conecte sua conta GitHub.
4. Escolha **New > Blueprint**, selecione o repositório e confirme a configuração indicada em `render.yaml`.
5. Aguarde a publicação. O Render fornecerá uma URL pública com HTTPS, normalmente terminada em `.onrender.com`.
6. Abra a URL no celular com dados móveis e teste perguntas e fontes da Wikipédia.
7. Gere um QR Code apontando para a URL pública **depois** de confirmar que ela funciona.

**Atenção:** planos e disponibilidade de hospedagem gratuita podem mudar. No plano gratuito, o serviço pode entrar em suspensão por inatividade e demorar a responder no primeiro acesso. Um domínio personalizado é opcional e pode ter custo.

## Alternativa: configuração manual

Se não usar Blueprint, crie um Web Service Python, com:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --bind 0.0.0.0:$PORT app:app`
- Health check path: `/health`
- Variável de ambiente `SECRET_KEY`: gere um valor aleatório e mantenha privado.

## Limites

A pesquisa online utiliza a Wikipédia em português, não uma IA generativa. O aplicativo não tem contas de usuários, painel administrativo ou banco de dados persistente. Se houver muitos acessos simultâneos, a capacidade dependerá do plano contratado.
