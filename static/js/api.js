/**
 * EduEvent – API Client
 * Replaces localStorage with Django REST API calls.
 * All dashboard pages use this instead of the old db.js.
 */

const API = {
  BASE: '',

  // ── HTTP Helpers ──────────────────────────────────────────────
  async _fetch(url, options = {}) {
    const defaults = {
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.getCSRF() },
      credentials: 'include',
    };
    const res = await fetch(this.BASE + url, { ...defaults, ...options });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
  },

  async get(url) {
    return this._fetch(url);
  },

  async post(url, body = {}) {
    return this._fetch(url, { method: 'POST', body: JSON.stringify(body) });
  },

  getCSRF() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
  },

  // ── Auth ──────────────────────────────────────────────────────
  async register(data) {
    return this.post('/api/auth/register/', data);
  },

  async login(data) {
    return this.post('/api/auth/login/', data);
  },

  async logout() {
    await this.post('/api/auth/logout/');
    window.location.href = '/';
  },

  async me() {
    return this.get('/api/auth/me/');
  },

  // ── Events ────────────────────────────────────────────────────
  async getEvents(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.get(`/api/events/${qs ? '?' + qs : ''}`);
  },

  async createEvent(data) {
    return this.post('/api/events/create/', data);
  },

  async updateEvent(eventId, data) {
    return this.post(`/api/events/${eventId}/update/`, data);
  },

  async approveEvent(eventId, note = '') {
    return this.updateEvent(eventId, { action: 'approve', note });
  },

  async rejectEvent(eventId, note = '') {
    return this.updateEvent(eventId, { action: 'reject', note });
  },

  async suggestDate(eventId, suggestedDate, suggestedVenueId, note = '') {
    return this.updateEvent(eventId, {
      action: 'suggest', suggested_date: suggestedDate,
      suggested_venue_id: suggestedVenueId, note,
    });
  },

  async makePublic(eventId, publicDescription = '') {
    return this.updateEvent(eventId, { action: 'make_public', public_description: publicDescription });
  },

  async deleteEvent(eventId) {
    return this.updateEvent(eventId, { action: 'delete' });
  },

  async hodRespondSuggestion(eventId, accept) {
    return this.post(`/api/events/${eventId}/hod-respond/`, { accept });
  },

  // ── Conflict Detection ────────────────────────────────────────
  async checkConflicts(venueId, date, endDate = '', excludeId = '') {
    const params = new URLSearchParams({ venue_id: venueId, date, end_date: endDate || date, exclude_id: excludeId });
    return this.get(`/api/conflicts/check/?${params}`);
  },

  async getAllConflicts() {
    return this.get('/api/conflicts/all/');
  },

  // ── Venues ────────────────────────────────────────────────────
  async getVenues() {
    return this.get('/api/venues/');
  },

  // ── Templates ─────────────────────────────────────────────────
  async getTemplates() {
    return this.get('/api/templates/');
  },

  async createTemplate(data) {
    return this.post('/api/templates/create/', data);
  },

  // ── Coordinators ──────────────────────────────────────────────
  async getCoordinatorRequests() {
    return this.get('/api/coordinators/');
  },

  async applyCoordinator(eventId, message = '') {
    return this.post('/api/coordinators/apply/', { event_id: eventId, message });
  },

  async updateCoordinator(reqId, status) {
    return this.post(`/api/coordinators/${reqId}/update/`, { status });
  },

  // ── Users ─────────────────────────────────────────────────────
  async getUsers(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.get(`/api/users/${qs ? '?' + qs : ''}`);
  },

  async approveUser(userId) {
    return this.post(`/api/users/${userId}/approve/`);
  },

  async deactivateUser(userId) {
    return this.post(`/api/users/${userId}/deactivate/`);
  },

  // ── Notifications ─────────────────────────────────────────────
  async getNotifications() {
    return this.get('/api/notifications/');
  },

  async markRead(notifId) {
    return this.post(`/api/notifications/${notifId}/read/`);
  },

  // ── Calendar ──────────────────────────────────────────────────
  async getCalendar(year) {
    return this.get(`/api/calendar/?year=${year || new Date().getFullYear()}`);
  },

  async createCalendarEntry(data) {
    return this.post('/api/calendar/create/', data);
  },

  async deleteCalendarEntry(entryId) {
    return this.post(`/api/calendar/${entryId}/delete/`);
  },

  // ── Analytics ─────────────────────────────────────────────────
  async getAnalytics() {
    return this.get('/api/analytics/');
  },

  // ── Branches ──────────────────────────────────────────────────
  async getBranches() {
    return this.get('/api/branches/');
  },
};

// ── Utility Functions ──────────────────────────────────────────

function fmtDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

function statusBadge(s) {
  const map = { pending: 'badge-pending', approved: 'badge-approved', rejected: 'badge-rejected' };
  return `<span class="badge ${map[s] || 'badge-pending'}">${s}</span>`;
}

function showError(el, msg) {
  el.textContent = msg;
  el.classList.add('show');
}

function hideMsg(el) {
  el.classList.remove('show');
}

function showSuccess(el, msg) {
  el.textContent = msg;
  el.classList.add('show');
}
