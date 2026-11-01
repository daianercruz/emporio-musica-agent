
const chat = document.getElementById("chat");
const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const sendButton = document.getElementById("send");
const newChatButton = document.getElementById("new-chat");

let sessionId = null;
let isLoading = false;

function scrollToBottom() {
    chat.scrollTop = chat.scrollHeight;
}

function addMessage(text, role, loading = false) {
    const message = document.createElement("div");
    message.className = `message ${role}`;

    if (loading) {
        message.classList.add("loading");
    }

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    if (role === "assistant" && !loading && window.marked && window.DOMPurify) {
        const html = marked.parse(text);
        bubble.innerHTML = DOMPurify.sanitize(html);
    } else {
        bubble.textContent = text;
    }

    message.appendChild(bubble);
    chat.appendChild(message);

    scrollToBottom();

    return message;
}

function setLoading(value) {
    isLoading = value;
    sendButton.disabled = value;
    input.disabled = value;
    newChatButton.disabled = value;
}

async function sendMessage(text) {
    const message = text.trim();

    if (!message || isLoading) {
        return;
    }

    const welcome = document.getElementById("welcome");

    if (welcome) {
        welcome.remove();
    }

    addMessage(message, "user");

    input.value = "";
    input.style.height = "auto";

    setLoading(true);

    const loadingMessage = addMessage(
        "Téo está pensando...",
        "assistant",
        true
    );

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        sessionId = data.session_id;

        loadingMessage.remove();

        addMessage(
            data.response || "Não consegui gerar uma resposta.",
            "assistant"
        );
    } catch (error) {
        loadingMessage.remove();

        addMessage(
            "Desculpe, não consegui me conectar agora. Tente novamente em instantes.",
            "assistant"
        );

        console.error("Chat error:", error);
    } finally {
        setLoading(false);
        input.focus();
    }
}

function setupSuggestions() {
    document.querySelectorAll(".suggestion").forEach((button) => {
        button.addEventListener("click", () => {
            sendMessage(button.textContent.trim());
        });
    });
}

function resetChat() {
    if (isLoading) {
        return;
    }

    sessionId = null;

    chat.innerHTML = `
        <section id="welcome" class="welcome">
            <div class="welcome-icon">♫</div>
            <h2>Olá! Eu sou o Téo.</h2>
            <p>
                Seu assistente virtual da Empório da Música.
                Como posso ajudar você hoje?
            </p>
            <div class="suggestions">
                <button type="button" class="suggestion">
                    Quais produtos estão em promoção?
                </button>
                <button type="button" class="suggestion">
                    Vocês têm violões disponíveis?
                </button>
                <button type="button" class="suggestion">
                    Como funciona a devolução?
                </button>
                <button type="button" class="suggestion">
                    Quero consultar meu pedido.
                </button>
            </div>
        </section>
    `;

    input.value = "";
    setupSuggestions();
    input.focus();
}

form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage(input.value);
});

input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage(input.value);
    }
});

input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
});

newChatButton.addEventListener("click", resetChat);

setupSuggestions();
