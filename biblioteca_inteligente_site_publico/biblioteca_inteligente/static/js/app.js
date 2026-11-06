const form = document.querySelector("#question-form");
const input = document.querySelector("#question-input");
const askButton = document.querySelector("#ask-button");
const answerSection = document.querySelector("#answer-section");
const answerTitle = document.querySelector("#answer-title");
const answerBody = document.querySelector("#answer-body");
const clearButton = document.querySelector("#clear-button");
const copyButton = document.querySelector("#copy-button");
const toast = document.querySelector("#toast");
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
      body: JSON.stringify({question: trimmed})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Não foi possível pesquisar agora.");
    answerTitle.textContent = data.topic || "Sua resposta";
    renderAnswer(data.answer || "Não encontrei uma resposta.", data.sources || []);
    answerSection.hidden = false;
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

clearButton.addEventListener("click", async () => {
  try { await fetch("/api/reset", {method: "POST"}); } catch (_) {}
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
