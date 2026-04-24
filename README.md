# 🎓 EduEvent — Full-Stack College Event & Venue Management System

> **Project Code:** P-04  
> **Type:** Full-Stack Role-Based Web Application  
> **Tech Stack:** Django 5.1 · PostgreSQL (Supabase) · Firebase Authentication · HTML5/Vanilla JS  
> **Google Font:** Inter  

---

## 📌 Problem Statement

College events are often managed independently by departments, leading to scheduling conflicts, poor coordination, and reduced student participation. The absence of a centralized system makes it difficult to track venue availability and event approvals.

**EduEvent** solves this by providing a **unified, role-based web platform** to manage college events and venue bookings with proper approval workflows, server-side conflict-free scheduling, automated SMTP email notifications, and Firebase-secured authentication.

---

## 🚀 Tech Stack

- **Backend:** Django 5.1 (Python)
- **Database:** PostgreSQL (hosted on Supabase)
- **Authentication:** Firebase Email Authentication (Frontend JS SDK) paired with secure Django Sessions
- **Email Notifications:** Django SMTP backend triggering automated system emails
- **Frontend:** HTML5, Vanilla CSS (Custom Glassmorphism Design System), Vanilla JavaScript (`fetch` API)

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SURAJK191/20_WEB_TEJAX.git
   cd 20_WEB_TEJAX
   ```

2. **Set up Python Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows PowerShell
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory (alongside `manage.py`) based on the `.env.example` file. You will need:
   - Django Secret Key
   - Supabase Database URL (`DATABASE_URL`)
   - Firebase Client Configuration
   - SMTP Email Credentials (e.g., Gmail App Password)

5. **Run Database Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   Open `http://127.0.0.1:8000` in your web browser.

---

## 👑 Initializing Master Admin

To create your master admin account:
1. Run the server and go to `http://127.0.0.1:8000/pages/register.html`
2. Register a new account with your email address (acting as any role).
3. Open a new terminal window in your project folder and run:
   ```bash
   python promote_admin.py your_email@example.com
   ```
4. You can now log into the **Admin Portal** using this email.

---

## 👥 Roles & Access Levels

### 🛡️ Admin — Full System Access
- **Dashboard:** Live analytics, pending approvals, conflict alerts.
- **Event Approvals:** Approve/Reject HOD event requests with conflict warnings.
- **Conflict Detector:** Automatically detects venue/date scheduling overlaps using the PostgreSQL database.
- **Date Suggestion:** Send alternative date/venue suggestions back to HODs.
- **User Management:** Approve incoming registrations from Students, HODs, and Teachers.

### 🏛️ HOD (Head of Department)
- **Request Event:** Submit an event with live frontend conflict previews.
- **Admin Suggestions:** Accept or decline alternate dates suggested by the Admin.
- **Coordinator Requests:** Approve/Reject student coordinator applications.
- **Department Oversight:** Manage all branch events.

### 🎒 Student
- **Event Coordinator:** Apply to be a coordinator for upcoming events.
- **Browse Events:** View upcoming, past, and featured events.
- **My Applications:** Track status of coordinator requests.

### 📚 Teacher
- **Branch Tracking:** View events specifically organized by your branch.
- **Venue Schedule:** Read-only access to venue booking statuses.

---

## 🌐 Core System Workflows

### 1. The Event Lifecycle & Email Notifications
```text
HOD submits event
   ↓ (System triggers New Event Email to Admin)
Admin sees request (PENDING)
   ↓
APPROVE ────── OR ────── SUGGEST NEW DATE
   ↓                            ↓
Event LIVE           (Email sent to HOD with suggestion)
(Email to HOD)                  ↓
                     HOD accepts suggestion → Event APPROVED
```

### 2. Secure Hybrid Authentication
```text
User fills Login Form
   ↓
Firebase JS SDK securely authenticates credentials
   ↓
Returns Firebase UID to Frontend
   ↓
Frontend POSTs Firebase UID to Django `/api/auth/login/`
   ↓
Django verifies UID against PostgreSQL UserProfile
   ↓
Django establishes secure HTTP-only Session Cookie
```

### 3. Public Interactive Wall
- A completely open, unauthenticated public view for students/parents to discover public events. 
- Features direct WhatsApp sharing links using dynamically generated event slugs (`/public/event/<slug>/`).

---

## 📁 System Architecture

```text
20_WEB_TEJAX/
│
├── manage.py                    ← Django entry point
├── eduevent/                    ← Core Django Settings & WSGI
│
├── core/                        ← Main Django Application
│   ├── models.py                ← PostgreSQL Schema (UserProfile, Event, Venue, etc)
│   ├── api_views.py             ← Complete REST API powering the frontend
│   ├── email_triggers.py        ← SMTP Notification Handlers
│   ├── email_service.py         ← HTML Email Compilers
│   └── views.py                 ← Template rendering routes
│
├── templates/                   ← Django HTML Templates
│   ├── dashboards/              ← Protected Role Dashboards
│   ├── email/                   ← Beautiful HTML Email Templates
│   ├── public/                  ← Public Event Wall
│   └── auth/                    ← Login / Register
│
└── js/db.js                     ← Frontend API Proxy (Replaced legacy localStorage)
```

---

## 🗄️ Database Design (PostgreSQL)

The primary tables handling application state:
- **`UserProfile`**: Stores Role, Branch, active-status, and linked `firebase_uid`.
- **`Event`**: Stores Date, Venue, HOD relationships, Status, robust fields.
- **`Venue`**: Fixed definitions for College Venues (Capacity, Name).
- **`CoordinatorRequest`**: Represents Many-to-Many junction between Student and Event.
- **`Notification`**: Real-time push notification tracking for the dashboard frontend.

---

## 🎨 Design System

- **Theme**: Premium Dark mode (deep navy `#0a0d1a`)
- **Card Style**: Glassmorphism with `backdrop-filter: blur`, modern CSS custom properties.
- **Animations**: Deep integration with `particles.js`, micro-interactions, pulse alerts, modal transitions.

---

## 📄 License & Credits

This project was developed for the **Artificial Intelligence Applications Lab**.

---

*Built with ❤️ using Python, Django, Supabase, and Vanilla JavaScript*

# 20_WEB_TEJAX