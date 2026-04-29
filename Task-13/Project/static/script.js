const chatForm = document.getElementById('chatForm');
const questionInput = document.getElementById('questionInput');
const chatContainer = document.getElementById('chatContainer');
const uploadForm = document.getElementById('uploadForm');
const uploadMessage = document.getElementById('uploadMessage');
const historyList = document.getElementById('historyList');
const typingIndicator = document.getElementById('typingIndicator');
const newChatBtn = document.getElementById('newChatBtn');
const homeState = document.getElementById('homeState');
const quickPrompts = document.querySelectorAll('.quick-prompt');

let historyData = [];
let draftThread = [];
let activeMode = 'history';

function toggleHomeState(visible) {
    if (!homeState) return;
    homeState.style.display = visible ? 'block' : 'none';
}

function formatTime(ts) {
    const d = ts ? new Date(ts.replace(' ', 'T')) : new Date();
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    return text
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function createMessage(role, content, timestamp) {
    const msg = document.createElement('article');
    msg.className = `message ${role}`;
    msg.innerHTML = `${escapeHtml(content).replaceAll('\n', '<br>')}<span class="time">${formatTime(timestamp)}</span>`;
    return msg;
}

function addMessage(role, content, timestamp) {
    const msg = createMessage(role, content, timestamp);
    chatContainer.appendChild(msg);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function renderThread(messages) {
    chatContainer.innerHTML = '';

    if (!messages.length) {
        toggleHomeState(true);
        return;
    }

    toggleHomeState(false);
    messages.forEach((item) => {
        addMessage(item.role, item.content, item.timestamp);
    });
}

function buildHistoryThread() {
    const thread = [];
    historyData.forEach((item) => {
        thread.push({ role: 'user', content: item.question, timestamp: item.timestamp });
        thread.push({ role: 'ai', content: item.answer, timestamp: item.timestamp });
    });
    return thread;
}

function refreshActiveChat() {
    if (activeMode === 'new') {
        renderThread(draftThread);
        return;
    }
    renderThread(buildHistoryThread());
}

function renderHistoryList() {
    historyList.innerHTML = '';
    const list = [...historyData].reverse();

    list.forEach((item) => {
        const card = document.createElement('button');
        card.className = `history-item ${activeMode === 'history' ? 'active' : ''}`;
        card.type = 'button';
        card.innerHTML = `
            <p class="history-q">${escapeHtml(item.question.slice(0, 72))}${item.question.length > 72 ? '...' : ''}</p>
            <p class="history-time">${new Date(item.timestamp.replace(' ', 'T')).toLocaleString()}</p>
        `;

        card.addEventListener('click', () => {
            activeMode = 'history';
            draftThread = [];
            renderHistoryList();
            refreshActiveChat();
        });

        historyList.appendChild(card);
    });
}

function setTyping(visible) {
    typingIndicator.classList.toggle('hidden', !visible);
}

async function loadHistory() {
    const response = await fetch('/history');
    const result = await response.json();

    if (!result.success || !Array.isArray(result.history)) {
        return;
    }

    historyData = result.history;
    renderHistoryList();
    refreshActiveChat();
}

chatForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const question = questionInput.value.trim();
    if (!question) return;

    const now = new Date().toISOString();
    if (activeMode === 'new') {
        draftThread.push({ role: 'user', content: question, timestamp: now });
        refreshActiveChat();
    } else {
        addMessage('user', question, now);
    }

    questionInput.value = '';
    setTyping(true);

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question }),
        });
        const result = await response.json();

        if (result.success) {
            const answerAt = new Date().toISOString();
            if (activeMode === 'new') {
                draftThread.push({ role: 'ai', content: result.answer, timestamp: answerAt });
                refreshActiveChat();
            } else {
                addMessage('ai', result.answer, answerAt);
            }
        } else {
            const errorAt = new Date().toISOString();
            if (activeMode === 'new') {
                draftThread.push({ role: 'ai', content: result.message || 'Failed to get answer.', timestamp: errorAt });
                refreshActiveChat();
            } else {
                addMessage('ai', result.message || 'Failed to get answer.', errorAt);
            }
        }
    } catch (error) {
        const networkAt = new Date().toISOString();
        if (activeMode === 'new') {
            draftThread.push({ role: 'ai', content: 'Network error. Please try again.', timestamp: networkAt });
            refreshActiveChat();
        } else {
            addMessage('ai', 'Network error. Please try again.', networkAt);
        }
    } finally {
        setTyping(false);
        loadHistory();
    }
});

newChatBtn?.addEventListener('click', () => {
    activeMode = 'new';
    draftThread = [];
    renderHistoryList();
    refreshActiveChat();
    questionInput?.focus();
});

quickPrompts.forEach((btn) => {
    btn.addEventListener('click', () => {
        const prompt = btn.dataset.prompt || '';
        if (!prompt || !questionInput) return;

        if (activeMode !== 'new') {
            activeMode = 'new';
            draftThread = [];
            renderHistoryList();
            refreshActiveChat();
        }

        questionInput.value = prompt;
        questionInput.focus();
    });
});

uploadForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    uploadMessage.textContent = 'Uploading and indexing...';

    const formData = new FormData(uploadForm);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });
        const result = await response.json();

        if (result.success) {
            uploadMessage.textContent = result.message;
            uploadForm.reset();
        } else {
            uploadMessage.textContent = result.message || 'Upload failed.';
        }
    } catch (error) {
        uploadMessage.textContent = 'Upload error. Please try again.';
    }
});

loadHistory();
