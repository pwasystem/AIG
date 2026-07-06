// ESTADO GLOBAL DA APLICAÇÃO
const state = {
    sessionId: localStorage.getItem("primordial_session_id") || "",
    exibirNoConsole: false,
    conversas: []
};

// ELEMENTOS DOM
const DOM = {
    sessionDisplay: document.getElementById("session-display"),
    newChatBtn: document.getElementById("new-chat-btn"),
    conversasList: document.getElementById("conversas-list"),
    chatMessages: document.getElementById("chat-messages"),
    chatInput: document.getElementById("chat-input"),
    sendBtn: document.getElementById("send-btn"),
    loadingCognitive: document.getElementById("loading-cognitive"),
    loadingStatus: document.getElementById("loading-status"),
    learnToggle: document.getElementById("learn-toggle"),
    
    // Accordions do painel cognitivo
    accordionHeaders: document.querySelectorAll(".accordion-header"),
    ragContent: document.querySelector("#cog-rag .accordion-content"),
    webContent: document.querySelector("#cog-web .accordion-content"),
    debateContent: document.querySelector("#cog-debate .accordion-content"),
    ethicsContent: document.querySelector("#cog-ethics .accordion-content")
};

// INICIALIZAÇÃO
document.addEventListener("DOMContentLoaded", () => {
    initApp();
    setupEventListeners();
    loadFiles();
});

// FUNÇÕES DE INICIALIZAÇÃO
function initApp() {
    // Atualiza o display de sessão
    if (state.sessionId) {
        DOM.sessionDisplay.textContent = state.sessionId.substring(0, 8) + "...";
    } else {
        DOM.sessionDisplay.textContent = "Sem sessão";
    }
    
    // Configura o Marked.js para quebras de linha normais
    marked.setOptions({
        breaks: true,
        gfm: true
    });
}

function setupEventListeners() {
    // Tecla Enter para enviar (com Shift+Enter para nova linha)
    DOM.chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Clique no botão Enviar
    DOM.sendBtn.addEventListener("click", sendMessage);

    // Clique em Nova Conversa (Reset)
    DOM.newChatBtn.addEventListener("click", resetSession);

    // Accordions Cognitivos (Direita)
    DOM.accordionHeaders.forEach(header => {
        header.addEventListener("click", () => {
            const item = header.parentElement;
            item.classList.toggle("active");
        });
    });

    // Toggle de log do console
    DOM.learnToggle.addEventListener("change", (e) => {
        state.exibirNoConsole = e.target.checked;
        const cmd = state.exibirNoConsole ? "#learn_on" : "#learn_off";
        sendSilentCommand(cmd);
    });
}

// LOGICA DE SESSÃO E ENVIO
async function sendMessage() {
    const text = DOM.chatInput.value.trim();
    if (!text) return;

    // Limpa o input
    DOM.chatInput.value = "";
    
    // Adiciona a mensagem do usuário na tela
    appendMessage("user", text);
    
    // Se for um comando direto digitado, trata localmente
    if (text === "#learn_on") {
        state.exibirNoConsole = true;
        DOM.learnToggle.checked = true;
        appendMessage("system", "👁️ Modo Aprendizado ATIVADO no console do servidor.");
        return;
    }
    if (text === "#learn_off") {
        state.exibirNoConsole = false;
        DOM.learnToggle.checked = false;
        appendMessage("system", "👁️ Modo Aprendizado DESATIVADO no console do servidor.");
        return;
    }

    // Exibe o carregamento cognitivo
    showLoading("Pesquisando memórias e referências...");

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: state.sessionId,
                message: text
            })
        });

        if (!response.ok) {
            throw new Error("Erro de comunicação com o servidor.");
        }

        const data = await response.json();
        
        // Atualiza a sessão se for nova
        if (!state.sessionId || state.sessionId !== data.session_id) {
            state.sessionId = data.session_id;
            localStorage.setItem("primordial_session_id", state.sessionId);
            DOM.sessionDisplay.textContent = state.sessionId.substring(0, 8) + "...";
        }

        const resultado = data.resultado;
        hideLoading();

        if (resultado.sucesso) {
            appendMessage("bot", resultado.resposta_final);
            updateCognitivePanel(resultado);
            loadFiles();
        } else {
            const erroMsg = resultado.erro || "Falha desconhecida no ciclo de processamento.";
            appendMessage("system", `⚠️ [BLOQUEIO/IMPASSE]: ${erroMsg}`);
            updateCognitivePanel(resultado);
        }

    } catch (error) {
        hideLoading();
        appendMessage("system", `❌ Erro: ${error.message}`);
    }
}

async function sendSilentCommand(cmd) {
    try {
        await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: state.sessionId,
                message: cmd
            })
        });
    } catch (e) {
        console.error("Erro ao enviar comando silencioso:", e);
    }
}

async function resetSession() {
    if (!state.sessionId) return;
    
    if (confirm("Deseja limpar o histórico e iniciar uma nova sessão de conversa?")) {
        try {
            await fetch("/api/chat/reset", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: state.sessionId })
            });
            
            // Limpa mensagens do chat
            DOM.chatMessages.innerHTML = `
                <div class="message system-message">
                    <div class="message-content">
                        <h3>Conversa Redefinida 🧹</h3>
                        <p>Memória de curto prazo limpa. O Samurai Digital está pronto para debater um novo assunto.</p>
                    </div>
                </div>
            `;
            
            clearCognitivePanel();
            
        } catch (error) {
            alert("Erro ao redefinir sessão: " + error.message);
        }
    }
}

// FORMATADORES E RENDERIZADORES
function appendMessage(role, text) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${role}-message`;
    
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    
    if (role === "system") {
        contentDiv.textContent = text;
    } else {
        contentDiv.innerHTML = marked.parse(text);
    }
    
    messageDiv.appendChild(contentDiv);
    DOM.chatMessages.appendChild(messageDiv);
    DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
}

function updateCognitivePanel(resultado) {
    if (resultado.contexto_rag && resultado.contexto_rag !== "Nenhum histórico ou padrão arquitetural registrado na memória de longo prazo ainda.") {
        DOM.ragContent.innerHTML = formatRAG(resultado.contexto_rag);
        document.getElementById("cog-rag").classList.add("active");
    } else {
        DOM.ragContent.innerHTML = `<div class="empty-cog-state">Nenhuma memória prévia resgatada do banco de dados vetorial.</div>`;
    }

    if (resultado.contexto_cientifico && resultado.contexto_cientifico !== "Nenhum artigo científico ou tese relevante foi localizado na internet.") {
        DOM.webContent.innerHTML = formatWebContent(resultado.contexto_cientifico);
        document.getElementById("cog-web").classList.add("active");
    } else {
        DOM.webContent.innerHTML = `<div class="empty-cog-state">Nenhum artigo ou tese científica correspondente foi resgatado na internet.</div>`;
    }

    if (resultado.historico_debate && resultado.historico_debate.length > 0) {
        DOM.debateContent.innerHTML = formatDebate(resultado.historico_debate);
        document.getElementById("cog-debate").classList.add("active");
    } else {
        DOM.debateContent.innerHTML = `<div class="empty-cog-state">Sem ciclos de debate registrados na transação atual.</div>`;
    }

    if (resultado.avaliacao_etica) {
        DOM.ethicsContent.innerHTML = formatEthics(resultado.avaliacao_etica);
        document.getElementById("cog-ethics").classList.add("active");
    } else {
        DOM.ethicsContent.innerHTML = `<div class="empty-cog-state">Nenhuma introspecção moral realizada.</div>`;
    }
}

function clearCognitivePanel() {
    const emptyState = `<div class="empty-cog-state">Sem dados para a transação atual.</div>`;
    DOM.ragContent.innerHTML = emptyState;
    DOM.webContent.innerHTML = emptyState;
    DOM.debateContent.innerHTML = emptyState;
    DOM.ethicsContent.innerHTML = emptyState;
    
    document.querySelectorAll(".accordion-item").forEach(item => item.classList.remove("active"));
}

function formatRAG(ragText) {
    const memorias = ragText.split("---");
    return memorias.map(m => {
        if (!m.trim()) return "";
        const lines = m.trim().split("\n");
        const metaLine = lines[0];
        const content = lines.slice(1).join("\n");
        
        return `
            <div class="cog-card">
                <h4>Memória Recuperada</h4>
                <span class="meta">${metaLine}</span>
                <p>${content}</p>
            </div>
        `;
    }).join("");
}

function formatWebContent(webText) {
    const items = webText.split(/\[\d+\]/);
    let html = "";
    let index = 1;
    
    items.forEach(item => {
        if (!item.trim()) return;
        const lines = item.trim().split("\n");
        let title = "Artigo Acadêmico";
        let link = "#";
        let summary = "";
        
        lines.forEach(l => {
            if (l.startsWith(" Título:") || l.startsWith("Título:")) {
                title = l.replace(/.*Título:/, "").trim();
            } else if (l.startsWith(" Link:") || l.startsWith("Link:")) {
                link = l.replace(/.*Link:/, "").trim();
            } else if (l.startsWith(" Resumo:") || l.startsWith("Resumo:")) {
                summary = l.replace(/.*Resumo:/, "").trim();
            } else if (l.trim()) {
                summary += " " + l.trim();
            }
        });
        
        html += `
            <div class="cog-card">
                <h4>[${index++}] ${title}</h4>
                <p>${summary}</p>
                <a href="${link}" target="_blank">🔗 Acessar Fonte Científica</a>
            </div>
        `;
    });
    
    return html || `<p>${webText}</p>`;
}

function formatDebate(debateArray) {
    return debateArray.map(d => {
        const badgeClass = d.aprovado ? "aprovado" : "rejeitado";
        const badgeText = d.aprovado ? "APROVADO" : "REJEITADO";
        
        return `
            <div class="debate-step">
                <h4>Ciclo de Debate ${d.ciclo} <span class="badge ${badgeClass}">${badgeText}</span></h4>
                <div class="box">
                    <strong>Rascunho do Estudante (Ator):</strong>
                    <p style="font-size:11px; margin-top:4px; max-height:80px; overflow-y:auto; word-break:break-word;">
                        ${d.estudante.substring(0, 150)}...
                    </p>
                </div>
                <div class="box critica">
                    <strong>Crítica do Professor (Crítico):</strong>
                    <p style="font-size:11px; margin-top:4px;">${d.professor}</p>
                </div>
            </div>
        `;
    }).join("");
}

function formatEthics(ethics) {
    const isAlinhado = ethics.alinhado_com_a_luz && !ethics.viola_virtude_bushido;
    const statusClass = isAlinhado ? "alinhado" : "bloqueado";
    const statusText = isAlinhado ? "Aprovado pelo Axioma Zero (Luz)" : "Bloqueado por Violação Moral";
    const statusEmoji = isAlinhado ? "✅" : "🚨";
    
    return `
        <div class="ethics-box">
            <div class="ethics-status ${statusClass}">
                <span>${statusEmoji}</span> ${statusText}
            </div>
            <div class="ethics-analysis">
                <strong>Análise Filosófica de Impacto:</strong>
                <p style="margin-top:6px;">${ethics.analise_de_impacto || ethics.analise_impacto}</p>
            </div>
            ${ethics.justificativa_correcao && ethics.justificativa_correcao !== "Nenhuma" ? `
                <div class="ethics-analysis" style="border-left: 2px solid var(--accent-red)">
                    <strong>Ação de Correção Necessária:</strong>
                    <p style="margin-top:6px;">${ethics.justificativa_correcao}</p>
                </div>
            ` : ""}
        </div>
    `;
}

// CONTROLES DE CARREGAMENTO COGNITIVO
function showLoading(statusText) {
    DOM.loadingStatus.textContent = statusText;
    DOM.loadingCognitive.style.display = "flex";
    DOM.sendBtn.disabled = true;
    DOM.chatInput.disabled = true;
}

function hideLoading() {
    DOM.loadingCognitive.style.display = "none";
    DOM.sendBtn.disabled = false;
    DOM.chatInput.disabled = false;
    DOM.chatInput.focus();
}

// BUSCA DE ARQUIVOS GERADOS AGRUPADOS
async function loadFiles() {
    try {
        const response = await fetch("/api/files");
        if (!response.ok) return;
        
        const data = await response.json();
        state.conversas = data.conversas || [];
        
        renderConversasList();
    } catch (e) {
        console.error("Erro ao buscar lista de arquivos agrupados:", e);
    }
}

function renderConversasList() {
    if (state.conversas.length === 0) {
        DOM.conversasList.innerHTML = `<div class="empty-list">Nenhuma conversa gerada.</div>`;
        return;
    }

    DOM.conversasList.innerHTML = state.conversas.map(conversa => {
        const isCurrentSession = conversa.session_id === state.sessionId;
        const activeClass = isCurrentSession ? "active" : "";
        
        // Mapeia respostas e programas da conversa
        const listaArquivos = [];
        
        conversa.respostas.forEach(r => {
            const sizeKB = (r.size / 1024).toFixed(1);
            listaArquivos.push(`
                <li onclick="downloadFile('${conversa.session_id}', 'respostas', '${r.name}')">
                    <span class="file-name">📄 ${r.name}</span>
                    <div class="file-meta">
                        <span>${sizeKB} KB</span>
                        <span>${r.date}</span>
                    </div>
                </li>
            `);
        });

        conversa.programas.forEach(p => {
            const sizeKB = (p.size / 1024).toFixed(1);
            listaArquivos.push(`
                <li onclick="downloadFile('${conversa.session_id}', 'programas', '${p.name}')">
                    <span class="file-name">🐍 ${p.name}</span>
                    <div class="file-meta">
                        <span>${sizeKB} KB</span>
                        <span>${p.date}</span>
                    </div>
                </li>
            `);
        });

        return `
            <div class="conversa-item ${activeClass}" id="conv-${conversa.session_id}">
                <div class="conversa-header" onclick="toggleConversa('${conversa.session_id}')">
                    <span class="title-text" title="${conversa.titulo}">💬 ${conversa.titulo}</span>
                    <span class="chevron">▼</span>
                </div>
                <ul class="conversa-files">
                    ${listaArquivos.join("")}
                </ul>
            </div>
        `;
    }).join("");
}

function toggleConversa(sessionId) {
    const item = document.getElementById(`conv-${sessionId}`);
    if (item) {
        item.classList.toggle("active");
    }
}

function downloadFile(sessionId, tipo, filename) {
    window.open(`/api/files/download/${sessionId}/${tipo}/${filename}`, "_blank");
}
