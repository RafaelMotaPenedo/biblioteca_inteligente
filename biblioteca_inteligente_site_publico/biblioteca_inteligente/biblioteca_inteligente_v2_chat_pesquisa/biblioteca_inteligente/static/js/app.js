const form = document.querySelector("#question-form");
const input = document.querySelector("#question-input");
const askButton = document.querySelector("#ask-button");
const answerSection = document.querySelector("#answer-section");
const answerTitle = document.querySelector("#answer-title");
const answerBody = document.querySelector("#answer-body");
const clearButton = document.querySelector("#clear-button");
const copyButton = document.querySelector("#copy-button");
const toast = document.querySelector("#toast");
const modeSelect = document.querySelector('#research-mode');
const conversation = document.querySelector('#conversation');
const resetChat = document.querySelector('#reset-chat');
let history = [];
let lastAnswer = "";
let toastTimer;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
}

function safeText(text) {
  // Render text only; do not inject server output as HTML.
  return document.createTextNode(text);
}

function renderAnswer(text, sources = []) {
  answerBody.replaceChildren();
  text.split(/\n{2,}/).filter(Boolean).forEach((paragraph) => {
    const p = document.createElement("p");
    p.className = "answer-paragraph";
    p.appendChild(safeText(paragraph));
    answerBody.appendChild(p);
  });
  if (sources.length) {
    const heading = document.createElement("p");
    heading.textContent = "Fontes consultadas:";
    heading.style.fontWeight = "bold";
    answerBody.appendChild(heading);
    sources.forEach((source) => {
      const p = document.createElement("p");
      const a = document.createElement("a");
      a.textContent = source.title;
      a.href = source.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      p.appendChild(a);
      answerBody.appendChild(p);
    });
  }
  lastAnswer = text;
}

async function askQuestion(question) {
  const trimmed = question.trim();
  if (!trimmed) {
    input.focus();
    return;
  }
  askButton.disabled = true;
  askButton.querySelector("span").textContent = "Pesquisando…";
  input.value = trimmed;
  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: trimmed, mode: modeSelect.value})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Não foi possível pesquisar agora.");
    answerTitle.textContent = data.topic || "Sua resposta";
    renderAnswer(data.answer || "Não encontrei uma resposta.", data.sources || []);
    answerSection.hidden = false;
    history.push({question: trimmed, answer: data.answer || '', engine: data.engine || '', sources: data.sources || []});
    if (history.length > 20) history.shift();
    renderHistory();
    answerSection.scrollIntoView({behavior: "smooth", block: "start"});
  } catch (error) {
    showToast(error.message || "Falha de conexão. Tente novamente.");
  } finally {
    askButton.disabled = false;
    askButton.querySelector("span").textContent = "Investigar";
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  askQuestion(input.value);
});

document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => askQuestion(button.dataset.question));
});

function renderHistory() {
  conversation.replaceChildren();
  history.forEach((item) => {
    const article = document.createElement('article');
    article.className = 'chat-entry';
    const q = document.createElement('div');
    q.className = 'chat-question';
    q.textContent = 'Pergunta: ' + item.question;
    const a = document.createElement('div');
    a.className = 'chat-response';
    a.textContent = item.answer;
    const meta = document.createElement('div');
    meta.className = 'chat-meta';
    meta.textContent = 'Fonte: ' + item.engine;
    article.append(q, a, meta);
    if (item.sources.length) {
      const links = document.createElement('div');
      links.className = 'chat-sources';
      item.sources.forEach((source) => {
        if (!source.url || !source.url.startsWith('https://pt.wikipedia.org/wiki/')) return;
        const link = document.createElement('a');
        link.href = source.url;
        link.textContent = source.title;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        links.appendChild(link);
      });
      article.appendChild(links);
    }
    conversation.appendChild(article);
  });
}

resetChat.addEventListener('click', async () => {
  history = [];
  renderHistory();
  try { await fetch('/api/reset', {method: 'POST'}); } catch (_) {}
  answerSection.hidden = true;
  answerBody.replaceChildren();
  input.value = '';
  input.focus();
  showToast('Conversa limpa.');
});

clearButton.addEventListener("click", async () => {
  answerSection.hidden = true;
  answerBody.replaceChildren();
  input.value = "";
  input.focus();
  window.scrollTo({top: document.querySelector(".workspace").offsetTop - 16, behavior: "smooth"});
});

copyButton.addEventListener("click", async () => {
  if (!lastAnswer) return;
  try {
    await navigator.clipboard.writeText(lastAnswer);
    showToast("Resposta copiada.");
  } catch (_) {
    showToast("Seu navegador não permitiu copiar. Selecione o texto da resposta.");
  }
});
