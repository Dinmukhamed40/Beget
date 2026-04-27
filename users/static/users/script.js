// --- ЧАТ-ВИДЖЕТ S.H.I.E.L.D. HELPLINE ---

function toggleChat() {
    const win = document.getElementById('chatWindow');
    if (win) {
        const isHidden = window.getComputedStyle(win).display === 'none';
        win.style.display = isHidden ? 'flex' : 'none';
    }
}

function sendWidgetMessageAdapter() {
    const tokenEl = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!tokenEl) {
        console.error('CSRF token не найден!');
        return;
    }
    sendWidgetMessage(tokenEl.value, '/chat/');
}

function sendWidgetMessage(csrfToken, chatUrl) {
    const input = document.getElementById('widget-input');
    const log = document.getElementById('widget-chat-log');

    if (!input || !log || !input.value.trim()) return;

    const msg = input.value.trim();
    input.value = '';

    // Сообщение пользователя
    log.innerHTML += `<div style="text-align:right;margin-bottom:10px;">
        <span style="background:#333;color:#fff;padding:5px 12px;border-radius:15px;display:inline-block;font-size:14px;">${escapeHtml(msg)}</span>
    </div>`;
    log.scrollTop = log.scrollHeight;

    // Индикатор загрузки
    const loadingId = 'loading-' + Date.now();
    log.innerHTML += `<div id="${loadingId}" style="color:#888;font-size:13px;margin-bottom:10px;">S.H.I.E.L.D: ...</div>`;
    log.scrollTop = log.scrollHeight;

    fetch(chatUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: 'message=' + encodeURIComponent(msg)
    })
    .then(res => {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
    })
    .then(data => {
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();

        log.innerHTML += `<div style="color:#e62429;margin-bottom:10px;font-size:14px;">
            <b>S.H.I.E.L.D:</b> ${escapeHtml(data.reply)}
        </div>`;
        log.scrollTop = log.scrollHeight;

        // Озвучка ответа
        if (data.reply && typeof speak === 'function') speak(data.reply);
    })
    .catch(err => {
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();

        log.innerHTML += `<div style="color:orange;font-size:12px;margin-bottom:10px;">Ошибка связи с базой. Попробуй ещё раз.</div>`;
        log.scrollTop = log.scrollHeight;
        console.error('Ошибка чата:', err);
    });
}

// Защита от XSS — экранируем пользовательский ввод
function escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

// --- ГОЛОСОВОЙ ВВОД ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.lang = 'ru-RU';
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onstart = () => {
        const micIcon = document.getElementById('mic-icon');
        const micBtn = document.getElementById('widget-mic-btn');
        if (micIcon) micIcon.innerText = '🛑';
        if (micBtn) micBtn.style.boxShadow = '0 0 10px #e62429';
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const input = document.getElementById('widget-input');
        if (input) {
            input.value = transcript;
            setTimeout(() => sendWidgetMessageAdapter(), 500);
        }
    };

    recognition.onerror = (event) => {
        console.error('Ошибка микрофона:', event.error);
        if (event.error === 'not-allowed') {
            alert('Разрешите доступ к микрофону в настройках браузера!');
        }
    };

    recognition.onend = () => {
        const micIcon = document.getElementById('mic-icon');
        const micBtn = document.getElementById('widget-mic-btn');
        if (micIcon) micIcon.innerText = '🎤';
        if (micBtn) micBtn.style.boxShadow = 'none';
    };
}

function startVoiceInput() {
    if (recognition) {
        try { recognition.start(); }
        catch (e) { recognition.stop(); }
    } else {
        alert('Браузер не поддерживает голосовой ввод. Используйте Chrome.');
    }
}

// --- ВИКТОРИНА ---
let currentQuizStep = 0;

function nextStep() {
    const questions = document.querySelectorAll('.question-item');
    if (questions.length === 0) return;
    if (!questions[currentQuizStep].querySelector('input:checked')) {
        alert('Выберите вариант!');
        return;
    }
    questions[currentQuizStep].classList.remove('active');
    currentQuizStep++;
    if (currentQuizStep < questions.length) {
        questions[currentQuizStep].classList.add('active');
        const indicator = document.getElementById('step-indicator');
        if (indicator) indicator.innerText = `ВОПРОС ${currentQuizStep + 1} ИЗ 10`;
    }
}

function processFeedback() {
    const form = document.getElementById('feedback-form');
    const header = document.getElementById('quiz-header');
    const thankYou = document.getElementById('thank-you');

    if (form) form.style.display = 'none';
    if (header) header.style.display = 'none';
    if (thankYou) thankYou.style.display = 'block';

    const a = 0.2, b = 0.1, D = 754, W = 196;
    const time = a + b * Math.log2((D / W) + 1);

    const formula = document.getElementById('calc-formula');
    const result = document.getElementById('calc-result');
    if (formula) formula.innerText = `T = ${a} + ${b} * log2(${D}/${W} + 1)`;
    if (result) result.innerText = time.toFixed(3);
}

// --- НАСТРОЕНИЕ ---
function setMood(val) {
    const textElem = document.getElementById('user-text');
    if (textElem) {
        textElem.value = 'Я чувствую себя ' + val;
        analyzeMood();
    }
}

function analyzeMood() {
    const textElem = document.getElementById('user-text');
    const result = document.getElementById('mood-result');
    if (!textElem || !result) return;
    const text = textElem.value.toLowerCase();

    if (text.includes('эпич') || text.includes('отлич') || text.includes('нормально')) {
        result.innerText = 'СТАТУС: БОЕВАЯ ГОТОВНОСТЬ 🔥';
        result.style.color = '#00ff00';
    } else if (text.includes('плох') || text.includes('устал')) {
        result.innerText = 'СТАТУС: ТРЕБУЕТСЯ ПЕРЕЗАГРУЗКА 💀';
        result.style.color = '#e62429';
    } else {
        result.innerText = 'СТАТУС: АНАЛИЗ...';
        result.style.color = '#fff';
    }
}

function saveReport() {
    const text = document.getElementById('user-text');
    if (!text || !text.value.trim()) {
        alert('Введите текст отчёта!');
        return;
    }
    alert('Отчёт сохранён в базу, агент!');
}
