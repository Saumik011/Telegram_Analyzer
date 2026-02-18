const API_BASE = '/api';

// State
let currentChatId = null;
let chartInstance = null;

// Init
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    loadChats();
});

async function checkStatus() {
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();
        const statusEl = document.getElementById('auth-status');
        if (data.authorized) {
            statusEl.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-400"></span> Connected';
            statusEl.classList.add('text-emerald-400');
            document.getElementById('login-modal').classList.add('hidden');
        } else {
            statusEl.innerHTML = '<span class="w-2 h-2 rounded-full bg-rose-500"></span> Disconnected';
            statusEl.classList.add('text-rose-400');
            document.getElementById('login-modal').classList.remove('hidden');
        }
    } catch (e) {
        console.error("Status check failed", e);
    }
}

async function sendCode() {
    const phone = document.getElementById('phone-input').value;
    const btn = document.querySelector('#step-phone button');
    btn.disabled = true;
    btn.textContent = "Sending...";

    try {
        const res = await fetch(`${API_BASE}/login?phone=${encodeURIComponent(phone)}`, { method: 'POST' });
        if (res.ok) {
            document.getElementById('step-phone').classList.add('hidden');
            document.getElementById('step-code').classList.remove('hidden');
        } else {
            const err = await res.json();
            alert("Error: " + (err.detail || "Failed to send code"));
            btn.disabled = false;
            btn.textContent = "Send Verification Code";
        }
    } catch (e) {
        alert("Network Error");
        btn.disabled = false;
    }
}

async function verifyCode() {
    const phone = document.getElementById('phone-input').value;
    const code = document.getElementById('code-input').value;
    const password = document.getElementById('password-input').value;

    const res = await fetch(`${API_BASE}/verify?phone=${encodeURIComponent(phone)}&code=${encodeURIComponent(code)}&password=${encodeURIComponent(password)}`, { method: 'POST' });
    if (res.ok) {
        document.getElementById('login-modal').classList.add('hidden');
        checkStatus();
        loadChats(); // Reload chats after login
    } else {
        const err = await res.json();
        alert("Verification failed: " + err.detail);
    }
}

async function syncChats() {
    const btn = document.querySelector('button[onclick="syncChats()"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = `<svg class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Syncing...`;

    try {
        await fetch(`${API_BASE}/chats/sync`, { method: 'POST' });
        setTimeout(() => {
            loadChats();
            btn.innerHTML = originalText;
        }, 2000);
    } catch (e) {
        alert("Sync failed");
        btn.innerHTML = originalText;
    }
}

async function loadChats() {
    try {
        const res = await fetch(`${API_BASE}/chats`);
        const chats = await res.json();
        const list = document.getElementById('chat-list');
        list.innerHTML = '';

        if (chats.length === 0) {
            list.innerHTML = '<div class="text-center text-gray-600 mt-10 text-sm italic">No chats found. Try syncing.</div>';
            return;
        }

        chats.forEach(chat => {
            const div = document.createElement('div');
            // Check active state if implemented
            const isActive = currentChatId == chat.id;
            const bgClass = isActive ? 'bg-blue-600/20 border-blue-500/30' : 'hover:bg-slate-800/50 border-transparent';

            div.className = `p-3 rounded-lg cursor-pointer transition-all duration-200 border border-b border-gray-800/50 flex items-center gap-3 group ${bgClass}`;
            div.onclick = () => selectChat(chat.id, chat.title);

            // Random gradient for avatar base
            div.innerHTML = `
                <div class="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center font-bold text-gray-300 group-hover:text-white group-hover:bg-indigo-500 transition-colors shadow-inner text-sm ring-1 ring-white/10">
                    ${chat.title.charAt(0).toUpperCase()}
                </div>
                <div class="flex-1 overflow-hidden">
                    <div class="font-medium truncate text-gray-200 group-hover:text-white transition-colors">${chat.title}</div>
                    <div class="text-xs text-gray-500 group-hover:text-gray-400 capitalize flex items-center gap-1">
                        ${chat.type} 
                    </div>
                </div>
            `;
            list.appendChild(div);
        });
    } catch (e) {
        console.error("Load chats error", e);
    }
}

async function selectChat(chatId, title) {
    currentChatId = chatId;

    // UI Updates
    document.getElementById('current-chat-title').textContent = title;
    document.getElementById('header-avatar').textContent = title.charAt(0).toUpperCase();
    document.getElementById('empty-state').classList.add('hidden');

    const dashboard = document.getElementById('dashboard-content');
    dashboard.classList.remove('hidden');
    // Small delay to allow display block to apply before opacity transition
    setTimeout(() => {
        dashboard.classList.remove('opacity-0');
    }, 10);

    // Trigger analysis
    await fetch(`${API_BASE}/chats/${chatId}/analyze`);

    // Fetch results
    loadChatResults(chatId);
}

async function loadChatResults(chatId) {
    if (currentChatId !== chatId) return; // Prevent race conditions

    const res = await fetch(`${API_BASE}/chats/${chatId}/results`);
    const messages = await res.json();

    updateMetrics(messages);
    renderMessages(messages);
    renderChart(messages);
}

function updateMetrics(messages) {
    if (!messages.length) return;

    // Msg Count
    document.getElementById('metric-msgs').textContent = messages.length;

    // Average Sentiment
    const totalSentiment = messages.reduce((sum, m) => sum + (m.sentiment || 0), 0);
    const avgSentiment = totalSentiment / messages.length;
    const sentimentEl = document.getElementById('metric-sentiment');
    const toneEl = document.getElementById('metric-tone');

    sentimentEl.textContent = avgSentiment.toFixed(2);

    // Colorize Sentiment
    if (avgSentiment > 0.05) { // Positive
        sentimentEl.className = "text-3xl font-bold text-emerald-400";
        toneEl.textContent = "Positive";
        toneEl.className = "text-sm font-medium text-emerald-300 mb-1 px-2 py-0.5 rounded bg-emerald-500/10";
    } else if (avgSentiment < -0.05) { // Negative
        sentimentEl.className = "text-3xl font-bold text-rose-400";
        toneEl.textContent = "Negative";
        toneEl.className = "text-sm font-medium text-rose-300 mb-1 px-2 py-0.5 rounded bg-rose-500/10";
    } else { // Neutral
        sentimentEl.className = "text-3xl font-bold text-gray-400";
        toneEl.textContent = "Neutral";
        toneEl.className = "text-sm font-medium text-gray-300 mb-1 px-2 py-0.5 rounded bg-gray-500/10";
    }

    // Average Urgency
    const totalUrgency = messages.reduce((sum, m) => sum + (m.urgency || 0), 0);
    const avgUrgency = totalUrgency / messages.length;
    document.getElementById('metric-urgency').textContent = Math.round(avgUrgency) + "%";
}

function renderMessages(messages) {
    const container = document.getElementById('message-list');
    container.innerHTML = '';

    messages.forEach(msg => {
        const div = document.createElement('div');
        const isSelf = false; // We don't have self-ID in this simplified view yet, assuming all aligned left for now or logic needed
        // Since we don't know "Self" easily without auth user ID, we'll align based on sentiment or just list them cleanly.
        // Actually, for a visual chat log, usually you want L/R alignment. 
        // Let's assume for now everything is "Incoming" style to be safe, but we'll check if we can infer.
        // We'll stick to a neutral "Stream" layout to avoid guessing wrong.

        div.className = "flex flex-col gap-1 w-full animate-fade-in";

        const sentimentColor = getSentimentColor(msg.sentiment);

        div.innerHTML = `
            <div class="msg-bubble glass-panel p-4 rounded-xl border border-gray-700/50 hover:bg-slate-800/80 transition-colors">
                 <div class="flex justify-between items-start mb-2">
                    <span class="text-xs font-bold text-gray-400 tracking-wide uppercase">${new Date(msg.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    <span class="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-gray-400">
                        ${msg.intent}
                    </span>
                 </div>
                 <div class="text-sm text-gray-200 leading-relaxed">${msg.text}</div>
                 
                 <!-- Footer Indicators -->
                 <div class="mt-3 flex items-center gap-3 pt-3 border-t border-gray-700/30">
                    <!-- Sentiment Indicator -->
                    <div class="flex items-center gap-1.5" title="Sentiment Score">
                        <div class="w-1.5 h-1.5 rounded-full ${sentimentColor.dot}"></div>
                        <span class="text-[10px] font-medium ${sentimentColor.text}">${msg.tone || 'Neutral'} (${(msg.sentiment || 0).toFixed(2)})</span>
                    </div>

                    <!-- Urgency Indicator -->
                    ${msg.urgency > 20 ? `
                    <div class="flex items-center gap-1.5" title="Urgency Score">
                        <div class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></div>
                        <span class="text-[10px] font-medium text-rose-300">High Urgency (${Math.round(msg.urgency)}%)</span>
                    </div>` : ''}
                 </div>
            </div>
        `;
        container.appendChild(div);
    });

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function getSentimentColor(score) {
    if (score > 0.05) return { dot: 'bg-emerald-400', text: 'text-emerald-300' };
    if (score < -0.05) return { dot: 'bg-rose-400', text: 'text-rose-300' };
    return { dot: 'bg-gray-400', text: 'text-gray-400' };
}

function renderChart(messages) {
    const ctx = document.getElementById('timelineChart').getContext('2d');

    if (chartInstance) chartInstance.destroy();

    const labels = messages.map(m => new Date(m.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    const urgencyData = messages.map(m => m.urgency || 0);
    const sentimentData = messages.map(m => (m.sentiment || 0) * 100); // Scale to match Urgency (0-100)

    // Gradient definitions
    const gradientUrgency = ctx.createLinearGradient(0, 0, 0, 400);
    gradientUrgency.addColorStop(0, 'rgba(244, 63, 94, 0.4)'); // Rose-500
    gradientUrgency.addColorStop(1, 'rgba(244, 63, 94, 0)');

    const gradientSentiment = ctx.createLinearGradient(0, 0, 0, 400);
    gradientSentiment.addColorStop(0, 'rgba(16, 185, 129, 0.4)'); // Emerald-500
    gradientSentiment.addColorStop(1, 'rgba(16, 185, 129, 0)');

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Urgency',
                    data: urgencyData,
                    borderColor: '#f43f5e', // Rose-500
                    backgroundColor: gradientUrgency,
                    borderWidth: 2,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Sentiment (Positivity)',
                    data: sentimentData,
                    borderColor: '#10b981', // Emerald-500
                    backgroundColor: gradientSentiment,
                    borderWidth: 2,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100, // Fixed scale for 0-100%
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        borderDash: [5, 5]
                    },
                    ticks: {
                        color: '#94a3b8', // Slate-400
                        font: { family: 'Outfit', size: 10 }
                    },
                    border: { display: false }
                },
                x: {
                    display: false // Hide x labels to reduce clutter
                }
            },
            plugins: {
                legend: {
                    display: false // We use our custom HTML legend
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 10,
                    titleFont: { family: 'Outfit', size: 12 },
                    bodyFont: { family: 'Outfit', size: 12 },
                    displayColors: true,
                    usePointStyle: true
                }
            }
        }
    });
}
