// SIH Single Page Application JavaScript Gateway
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initChat();
    loadTasks();
    loadApprovals();
    loadKnowledge();
    loadIntegrations();
    loadAuditLogs();
    loadSystemHealth();
});

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view-container');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const viewName = item.getAttribute('data-view');
            
            navItems.forEach(i => i.classList.remove('active'));
            views.forEach(v => v.classList.remove('active'));

            item.classList.add('active');
            document.getElementById(`view-${viewName}`).classList.add('active');
            document.getElementById('current-view-title').textContent = item.querySelector('span').textContent;
        });
    });
}

function initChat() {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    const history = document.getElementById('chat-history');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = input.value.trim();
        if (!prompt) return;

        // Append user bubble
        appendBubble('user', prompt);
        input.value = '';

        // Append typing indicator bubble
        const assistantBubble = appendBubble('assistant', 'Thinking & Resolving Context...');

        try {
            const response = await fetch('/api/v1/conversations/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: prompt })
            });

            const data = await response.json();
            assistantBubble.textContent = data.message;
            loadApprovals();
            loadTasks();
            loadAuditLogs();
        } catch (err) {
            assistantBubble.textContent = `Error: ${err.message}`;
        }
    });
}

function appendBubble(sender, content) {
    const history = document.getElementById('chat-history');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.textContent = content;
    history.appendChild(bubble);
    history.scrollTop = history.scrollHeight;
    return bubble;
}

async function loadTasks() {
    try {
        const res = await fetch('/api/v1/tasks');
        const tasks = await res.json();
        
        const todoCol = document.getElementById('tasks-todo');
        const inProgressCol = document.getElementById('tasks-inprogress');
        const doneCol = document.getElementById('tasks-done');

        todoCol.innerHTML = '';
        inProgressCol.innerHTML = '';
        doneCol.innerHTML = '';

        tasks.forEach(task => {
            const card = document.createElement('div');
            card.className = 'task-card';
            card.innerHTML = `
                <div class="task-priority ${task.priority}">${task.priority}</div>
                <strong>${task.title}</strong>
                <p style="font-size: 0.8rem; color: var(--text-secondary);">${task.description || 'No description'}</p>
            `;
            if (task.status === 'TODO') todoCol.appendChild(card);
            else if (task.status === 'IN_PROGRESS') inProgressCol.appendChild(card);
            else doneCol.appendChild(card);
        });
    } catch (e) { console.error('Failed to load tasks', e); }
}

async function loadApprovals() {
    try {
        const res = await fetch('/api/v1/approvals/pending');
        const approvals = await res.json();
        const container = document.getElementById('approvals-list');
        container.innerHTML = '';

        if (approvals.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.9rem;">No pending approvals in queue.</p>';
            return;
        }

        approvals.forEach(app => {
            const card = document.createElement('div');
            card.className = 'approval-card';
            card.innerHTML = `
                <div>
                    <strong style="color: var(--accent-amber);">${app.action_name}</strong> - Risk: <span style="color: var(--accent-rose); font-weight: bold;">${app.risk_level}</span>
                    <p style="font-size: 0.85rem; color: var(--text-secondary);">Target: ${app.target} | Requested: ${new Date(app.created_at).toLocaleTimeString()}</p>
                </div>
                <div class="approval-actions">
                    <button class="btn-success" onclick="reviewApproval('${app.id}', true)">Approve</button>
                    <button class="btn-danger" onclick="reviewApproval('${app.id}', false)">Reject</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (e) { console.error('Failed to load approvals', e); }
}

async function reviewApproval(approvalId, approve) {
    const endpoint = approve ? 'approve' : 'reject';
    await fetch(`/api/v1/approvals/${approvalId}/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewer_user_id: 'web-user' })
    });
    loadApprovals();
    loadAuditLogs();
}

async function loadKnowledge() {
    try {
        const res = await fetch('/api/v1/knowledge/search?q=');
        const docs = await res.json();
        const list = document.getElementById('knowledge-list');
        list.innerHTML = '';
        docs.forEach(doc => {
            const item = document.createElement('div');
            item.className = 'glass-card';
            item.style.marginBottom = '1rem';
            item.innerHTML = `
                <h4>${doc.title}</h4>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.5rem;">${doc.content}</p>
                <small style="color: var(--accent-blue); font-size: 0.75rem;">Source: ${doc.source_type}</small>
            `;
            list.appendChild(item);
        });
    } catch (e) { console.error(e); }
}

async function loadIntegrations() {
    try {
        const res = await fetch('/api/v1/integrations');
        const connectors = await res.json();
        const grid = document.getElementById('integrations-grid');
        grid.innerHTML = '';
        connectors.forEach(c => {
            const card = document.createElement('div');
            card.className = 'glass-card';
            card.innerHTML = `
                <h4>${c.name}</h4>
                <p style="font-size: 0.8rem; color: var(--text-secondary); margin: 0.5rem 0;">Connector ID: ${c.id}</p>
                <span class="status-badge" style="border-color: ${c.configured ? 'var(--accent-emerald)' : 'var(--text-muted)'}">
                    ${c.configured ? 'Configured' : 'Available'}
                </span>
            `;
            grid.appendChild(card);
        });
    } catch (e) { console.error(e); }
}

async function loadAuditLogs() {
    try {
        const res = await fetch('/api/v1/audit');
        const logs = await res.json();
        const tbody = document.getElementById('audit-table-body');
        tbody.innerHTML = '';
        logs.reverse().forEach(log => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="padding: 0.5rem; font-size: 0.8rem; border-bottom: 1px solid var(--glass-border);">${new Date(log.timestamp).toLocaleTimeString()}</td>
                <td style="padding: 0.5rem; font-size: 0.8rem; border-bottom: 1px solid var(--glass-border); font-weight: bold; color: var(--accent-blue);">${log.event_type}</td>
                <td style="padding: 0.5rem; font-size: 0.8rem; border-bottom: 1px solid var(--glass-border);">${log.producer}</td>
                <td style="padding: 0.5rem; font-size: 0.8rem; border-bottom: 1px solid var(--glass-border); color: ${log.status === 'SUCCESS' ? 'var(--accent-emerald)' : 'var(--accent-rose)'}">${log.status}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) { console.error(e); }
}

async function loadSystemHealth() {
    try {
        const res = await fetch('/api/v1/system/health');
        const data = await res.json();
        document.getElementById('sys-uptime').textContent = `${data.uptime_seconds.toFixed(0)}s`;
    } catch (e) { console.error(e); }
}
