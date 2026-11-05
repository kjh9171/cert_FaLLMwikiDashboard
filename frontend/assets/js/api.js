/* Family LLM WIKI - API Client */
const API_BASE = window.location.port === '8088'
  ? '/api/v1'
  : 'http://localhost:8088/api/v1';

let isOnline = false;

async function api(path, opts = {}) {
  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
    ...opts
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return res.json();
  return res.text();
}

async function checkBackend() {
  try {
    await api('/health');
    isOnline = true;
    const el = document.getElementById('backend-status');
    if (el) {
      el.textContent = 'Backend API Online';
      el.className = 'backend-status bg-emerald-100 text-emerald-700';
    }
  } catch (e) {
    isOnline = false;
    const el = document.getElementById('backend-status');
    if (el) {
      el.textContent = 'Backend Offline';
      el.className = 'backend-status bg-amber-100 text-amber-800';
    }
  }
}

/* ---------- Users ---------- */
async function fetchUsers() {
  return api('/users');
}
async function createUser(payload) {
  return api('/users', { method: 'POST', body: JSON.stringify(payload) });
}

/* ---------- Calendar ---------- */
async function fetchEvents(userId) {
  const qs = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
  return api(`/calendar/events${qs}`);
}
async function createEvent(payload) {
  return api('/calendar/events', { method: 'POST', body: JSON.stringify(payload) });
}
async function deleteEvent(id) {
  return api(`/calendar/events/${id}`, { method: 'DELETE' });

}

/* ---------- Todos ---------- */
async function fetchTodos(userId) {
  const qs = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
  return api(`/todos${qs}`);
}
async function createTodo(payload) {
  return api('/todos', { method: 'POST', body: JSON.stringify(payload) });
}
async function toggleTodo(id, completed) {
  return api(`/todos/${id}`, { method: 'PUT', body: JSON.stringify({ is_completed: completed }) });
}
async function deleteTodo(id) {
  return api(`/todos/${id}`, { method: 'DELETE' });
}

/* ---------- Finance ---------- */
async function fetchTransactions(userId) {
  const qs = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
  return api(`/finance/transactions${qs}`);
}
async function createTransaction(payload) {
  return api('/finance/transactions', { method: 'POST', body: JSON.stringify(payload) });
}
async function deleteTransaction(id) {
  return api(`/finance/transactions/${id}`, { method: 'DELETE' });
}

/* ---------- Storage helpers ---------- */
function getSelectedUserId() {
  return localStorage.getItem('selectedUserId') || '';
}
function setSelectedUserId(id) {
  localStorage.setItem('selectedUserId', id);
}
function clearSelectedUserId() {
  localStorage.removeItem('selectedUserId');
}

/* ---------- Modal helpers ---------- */
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}
function closeAllModals() {
  document.querySelectorAll('.modal-overlay').forEach(el => el.classList.remove('open'));
}

/* ---------- Format helpers ---------- */
function formatMoney(n) {
  return (n || 0).toLocaleString('ko-KR');
}
function formatDateTime(iso) {
  if (!iso) return '-';
  return new Date(iso).toLocaleString('ko-KR', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
function formatDate(iso) {
  if (!iso) return '-';
  return new Date(iso).toISOString().slice(0, 10);
}
