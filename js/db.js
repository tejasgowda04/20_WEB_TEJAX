/**
 * EduEvent – Django API-backed Database Client (Supabase)
 * This drops all localStorage usage. All data is fetched from Django 
 * (which uses Supabase). Local cache is purely for synchronous UI rendering.
 */

const DB = {
  KEYS: {
    ADMINS: 'edu_admins', HODS: 'edu_hods', STUDENTS: 'edu_students', TEACHERS: 'edu_teachers',
    EVENTS: 'edu_events', VENUES: 'edu_venues', COORD_REQ: 'edu_coord_requests', NOTIFICATIONS: 'edu_notifications',
  },
  BRANCHES: ['Computer Science','Information Technology','Electronics','Mechanical','Civil','Electrical','MBA','MCA'],
  VENUE_LIST: [
    { id:'V1', name:'Main Auditorium',   capacity:800,  description:'Main hall with stage & AV system' },
    { id:'V2', name:'Seminar Hall A',    capacity:200,  description:'AC seminar hall, ground floor' },
    { id:'V3', name:'Seminar Hall B',    capacity:200,  description:'AC seminar hall, first floor' },
    { id:'V4', name:'Open Ground',       capacity:2000, description:'Outdoor sports & cultural ground' },
    { id:'V5', name:'Conference Room',   capacity:50,   description:'Board room with projector' },
  ],

  _cache: { events: [], venues: [], users: [], coordRequests: [], notifications: [], loaded: false },
  _currentUser: null,

  async _fetch(url, options = {}) {
    try {
      const resp = await fetch(url, { credentials: 'include', headers: { 'Content-Type': 'application/json', ...options.headers }, ...options });
      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        return { _error: true, status: resp.status, ...data };
      }
      return await resp.json();
    } catch (e) { return { _error: true, message: e.message }; }
  },
  async _post(url, body) { return this._fetch(url, { method: 'POST', body: JSON.stringify(body) }); },
  _getCSRF() { const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken=')); return cookie ? cookie.split('=')[1] : ''; },
  async _postCSRF(url, body) {
    return this._fetch(url, { method: 'POST', body: JSON.stringify(body), headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this._getCSRF() } });
  },

  // ── INIT: Load ALL real-time data from Supabase/Django ─────────────────
  async init() {
    try {
      const [evRes, vRes, nRes, crRes, meRes] = await Promise.all([
        this._fetch('/api/events/'),
        this._fetch('/api/venues/'),
        this._fetch('/api/notifications/').catch(() => ({ notifications: [] })),
        this._fetch('/api/coordinators/').catch(() => ({ requests: [] })),
        this._fetch('/api/auth/me/').catch(() => ({ user: null }))
      ]);

      if (evRes.events) this._cache.events = evRes.events.map(e => this._normalizeEvent(e));
      if (vRes.venues && vRes.venues.length) this._cache.venues = vRes.venues;
      else this._cache.venues = this.VENUE_LIST;
      
      if (nRes.notifications) this._cache.notifications = nRes.notifications;
      if (crRes.requests) this._cache.coordRequests = crRes.requests;
      
      if (meRes.user) {
        this._currentUser = meRes.user;
        if (this._currentUser.role === 'admin') {
          const uRes = await this._fetch('/api/users/?t=' + Date.now());
          if (uRes.users) this._cache.users = uRes.users;
        }
      }
      this._cache.loaded = true;
    } catch (e) {
      console.warn('API init failed:', e);
      this._cache.venues = this.VENUE_LIST;
      this._cache.loaded = true;
    }
  },

  get(key) {
    if (key === this.KEYS.VENUES) return this._cache.venues;
    if (key === this.KEYS.EVENTS) return this._cache.events;
    if (key === this.KEYS.COORD_REQ) return this._cache.coordRequests;
    if (key === this.KEYS.NOTIFICATIONS) return this._cache.notifications;
    if (key === this.KEYS.ADMINS) return this._cache.users.filter(u => u.role === 'admin');
    if (key === this.KEYS.HODS) return this._cache.users.filter(u => u.role === 'hod');
    if (key === this.KEYS.STUDENTS) return this._cache.users.filter(u => u.role === 'student');
    if (key === this.KEYS.TEACHERS) return this._cache.users.filter(u => u.role === 'teacher');
    return [];
  },

  uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2,6).toUpperCase(); },

  currentUser() { return this._currentUser; },
  requireAuth(role) {
    if (!this._currentUser) { window.location.href = '../pages/login.html?role=' + role; return null; }
    if (role && this._currentUser.role !== role) { window.location.href = '../pages/login.html?role=' + role; return null; }
    return this._currentUser;
  },
  logout() {
    this._postCSRF('/api/auth/logout/', {}).finally(() => { window.location.href = '../index.html'; });
  },

  // ── Events CRUD ────────────────────────────────────────────────────────
  getEvents(filters = {}) {
    let events = [...this._cache.events];
    if (filters.status)   events = events.filter(e => e.status === filters.status);
    if (filters.branch)   events = events.filter(e => e.branch === filters.branch);
    if (filters.hodId)    events = events.filter(e => e.hodId === filters.hodId);
    if (filters.venueId)  events = events.filter(e => e.venueId === filters.venueId);
    if (filters.upcoming) events = events.filter(e => new Date(e.date) >= new Date(new Date().toDateString()));
    if (filters.past)     events = events.filter(e => new Date(e.date) < new Date(new Date().toDateString()));
    return events.sort((a,b) => new Date(a.date) - new Date(b.date));
  },

  addEvent(data) {
    const ev = { id: 'EVT_TEMP_' + this.uid(), ...data, status: 'pending', createdAt: new Date().toISOString() };
    this._cache.events.push(ev);

    // Call Supabase/Django API to persist
    return this._postCSRF('/api/events/create/', {
      title: ev.title, description: ev.description, date: ev.date, end_date: ev.endDate || ev.date,
      venue_id: ev.venueId, category: ev.category, expected_attendees: ev.expectedAttendees || 100,
      organizer: ev.organizer, branch: ev.branch
    }).then(res => {
      if (res && res.event) {
        const idx = this._cache.events.findIndex(e => e.id === ev.id);
        if (idx !== -1) {
            this._cache.events[idx] = this._normalizeEvent(res.event);
        } else {
            this._cache.events.push(this._normalizeEvent(res.event));
        }
        
        // Trigger Email Notification
        this._post('/api/email/new-event/', {
          title: ev.title, hod_name: ev.organizer, branch: ev.branch, date: ev.date, venue_name: ev.venueName
        });
        return res.event;
      }
      return res;
    });
  },

  deleteEvent(id) {
    this._cache.events = this._cache.events.filter(e => e.id !== id);
    this._postCSRF(`/api/events/${id}/update/`, { action: 'delete' });
  },

  detectConflicts(venueId, date, endDate, excludeId = null) {
    const events = this._cache.events.filter(e => e.status !== 'rejected' && e.venueId === venueId && e.id !== excludeId);
    const start = new Date(date), end = new Date(endDate || date);
    return events.filter(e => !(end < new Date(e.date) || start > new Date(e.endDate || e.date)));
  },

  approveEvent(id, note = '') {
    const ev = this._cache.events.find(e => e.id === id);
    if (!ev) return;
    ev.status = 'approved'; ev.adminNote = note;

    this._postCSRF(`/api/events/${id}/update/`, { action: 'approve', note }).then(res => {
      if (res && res.event) {
        ev.hod_email = res.event.hod_email; // Pass email from backend response if available
        this._post('/api/email/event-approved/', {
          title: ev.title, branch: ev.branch, date: ev.date, venue_name: ev.venueName,
          hod_email: ev.hod_email || '', admin_note: note
        });
      }
    });
    this.addNotification(ev.hodId, `"${ev.title}" has been APPROVED.`);
  },

  rejectEvent(id, note = '') {
    const ev = this._cache.events.find(e => e.id === id);
    if (!ev) return;
    ev.status = 'rejected'; ev.adminNote = note;

    this._postCSRF(`/api/events/${id}/update/`, { action: 'reject', note }).then(res => {
      if (res && res.event) {
         this._post('/api/email/event-rejected/', {
           title: ev.title, branch: ev.branch, date: ev.date,
           hod_email: res.event.hod_email || '', admin_note: note
         });
      }
    });
    this.addNotification(ev.hodId, `"${ev.title}" has been REJECTED.`);
  },

  suggestDate(id, newDate, newVenueId, note) {
    const ev = this._cache.events.find(e => e.id === id);
    if (!ev) return;
    const venue = this._cache.venues.find(v => v.id === newVenueId);
    ev.status = 'pending'; ev.suggestedDate = newDate; 
    ev.suggestedVenueId = newVenueId; ev.suggestedVenueName = venue ? venue.name : ev.venueName; ev.adminNote = note;

    this._postCSRF(`/api/events/${id}/update/`, { action: 'suggest', suggested_date: newDate, suggested_venue_id: newVenueId, note }).then(res => {
       if (res && res.event) {
         this._post('/api/email/date-suggestion/', {
           title: ev.title, date: ev.date, hod_email: res.event.hod_email || '',
           suggested_date: newDate, suggested_venue: venue ? venue.name : '', admin_note: note
         });
       }
    });
    this.addNotification(ev.hodId, `Admin suggested new date ${newDate} for "${ev.title}".`);
  },

  hodConfirmSuggestion(id, accept) {
    const ev = this._cache.events.find(e => e.id === id);
    if (!ev) return;
    if (accept) {
      ev.date = ev.suggestedDate || ev.date; ev.venueId = ev.suggestedVenueId || ev.venueId;
      ev.venueName = ev.suggestedVenueName || ev.venueName; ev.status = 'approved';
    } else { ev.status = 'pending'; }
    delete ev.suggestedDate; delete ev.suggestedVenueId; delete ev.suggestedVenueName;

    this._postCSRF(`/api/events/${id}/hod-respond/`, { accept });
    this.addNotification('admin', `HOD ${accept ? 'accepted' : 'declined'} the suggested date for "${ev.title}".`);
  },

  // ── Coordinators ────────────────────────────────────────────────────────
  getCoordRequests(filters = {}) {
    let reqs = [...this._cache.coordRequests];
    if (filters.studentId) reqs = reqs.filter(r => r.student_id === filters.studentId);
    if (filters.eventId)   reqs = reqs.filter(r => r.event_id === filters.eventId);
    if (filters.hodId)     reqs = reqs.filter(r => r.hod_id === filters.hodId);
    return reqs;
  },

  addCoordRequest(data) {
    const req = { id: 'CR_TEMP' + this.uid(), ...data, student_id: data.studentId, event_id: data.eventId, status: 'pending' };
    this._cache.coordRequests.push(req);

    this._postCSRF('/api/coordinators/apply/', { event_id: data.eventId, message: data.message || '' }).then(res => {
      this._post('/api/email/coordinator/', {
        action: 'applied', student_name: data.studentName, student_branch: data.studentBranch,
        event_title: data.eventTitle, hod_email: res.hod_email || ''
      });
    });
    this.addNotification(data.hodId, `Student ${data.studentName} applied for "${data.eventTitle}".`);
    return { success: true };
  },

  updateCoordRequest(id, status) {
    const req = this._cache.coordRequests.find(r => r.id === id);
    if (req) {
      req.status = status;
      this._postCSRF(`/api/coordinators/${id}/update/`, { status }).then(res => {
        this._post('/api/email/coordinator/', { action: status, student_email: res.student_email || '', event_title: res.event_title || '' });
      });
    }
  },

  // ── Users ───────────────────────────────────────────────────────────────
  getAllUsers() { return this._cache.users; },
  getPendingUsers() { return this._cache.users.filter(u => !u.is_approved); },
  approveUser(role, id) {
    const u = this._cache.users.find(u => u.id === id);
    if (u) {
      u.is_approved = true;
      this._postCSRF(`/api/users/${id}/approve/`, {}).then(() => {
        this._post('/api/email/user-approved/', { email: u.email, name: u.name, role: u.role });
      });
    }
  },
  deactivateUser(role, id) {
    const u = this._cache.users.find(u => u.id === id);
    if (u) { u.is_active = false; this._postCSRF(`/api/users/${id}/deactivate/`, {}); }
  },

  // ── Notifications ───────────────────────────────────────────────────────
  addNotification(target, message) {
    const notif = { id: 'N' + this.uid(), target, target_role: target, message, is_read: false, created_at: new Date().toISOString() };
    this._cache.notifications.unshift(notif);
  },
  getNotifications(target) {
    return this._cache.notifications.filter(n => n.target_role === target || n.target_role === 'all');
  },
  markNotifRead(id) {
    const n = this._cache.notifications.find(n => n.id === id);
    if (n) { n.is_read = true; this._postCSRF(`/api/notifications/${id}/read/`, {}); }
  },

  // ── Helpers ─────────────────────────────────────────────────────────────
  _normalizeEvent(e) {
    return {
      id: e.id, title: e.title, description: e.description, date: e.date, endDate: e.end_date,
      venueId: e.venue_id, venueName: e.venue_name, branch: e.branch, organizer: e.organizer,
      hodId: e.hod_id, status: e.status, category: e.category, expectedAttendees: e.expected_attendees,
      adminNote: e.admin_note, suggestedDate: e.suggested_date, suggestedVenueId: e.suggested_venue_id,
      suggestedVenueName: e.suggested_venue_name, is_public: e.is_public, public_slug: e.public_slug
    };
  }
};

(async function() {
  await DB.init();
  const ev = new Event('db-ready');
  window.dispatchEvent(ev);
})();
