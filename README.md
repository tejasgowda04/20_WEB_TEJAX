# 🎓 EduEvent — Unified College Event & Venue Management System

> **Project Code:** P-04  
> **Type:** Role-Based Web Application (Frontend Only – No Backend Required)  
> **Tech Stack:** HTML5 · Vanilla CSS · Vanilla JavaScript · localStorage  
> **Google Font:** Inter  

---

## 📌 Problem Statement

College events are often managed independently by departments, leading to scheduling conflicts, poor coordination, and reduced student participation. The absence of a centralized system makes it difficult to track venue availability and event approvals.

**EduEvent** solves this by providing a **unified, role-based web platform** to manage college events and venue bookings with proper approval workflows, conflict-free scheduling, and better coordination.

---

## 🚀 Quick Start

1. Navigate to the project folder:
   ```
   c:\Users\suraj\OneDrive\Desktop\event\
   ```
2. Open **`index.html`** (double-click or open in any browser)
3. Choose your role from the entry screen
4. Log in using the demo credentials below

> ⚠️ **No server or installation required.** Runs entirely in the browser using `localStorage` as the database.

---

## 🔐 Demo Login Credentials

| Role    | Email                      | Password   |
|---------|----------------------------|------------|
| 🛡️ Admin   | `admin@college.edu`        | `admin123` |
| 🏛️ HOD     | `hod.cs@college.edu`       | `hod123`   |
| 🏛️ HOD     | `hod.it@college.edu`       | `hod123`   |
| 🏛️ HOD     | `hod.ec@college.edu`       | `hod123`   |
| 🏛️ HOD     | `hod.mech@college.edu`     | `hod123`   |
| 🎒 Student  | `amit@student.edu`         | `stu123`   |
| 🎒 Student  | `priya@student.edu`        | `stu123`   |
| 📚 Teacher  | `anita@college.edu`        | `tch123`   |
| 📚 Teacher  | `vikas@college.edu`        | `tch123`   |

---

## 📁 Project File Structure

```
event/
│
├── index.html                   ← 🏠 Entry point — Role selector screen
├── welcome.html                 ← 🌟 Welcome / Landing page
├── README.md                    ← 📖 This file
│
├── css/
│   ├── main.css                 ← 🎨 Core design system (all dashboards)
│   └── welcome.css              ← 🎨 Welcome page styles
│
├── js/
│   ├── db.js                    ← 🗄️  Central localStorage database engine
│   ├── particles.js             ← ✨ Animated particle background
│   └── welcome.js               ← 🌟 Welcome page interactions
│
├── pages/
│   ├── login.html               ← 🔐 Universal login (role-aware)
│   ├── register.html            ← 📝 New member registration
│   ├── admin.html               ← 🛡️  Admin dashboard
│   ├── hod.html                 ← 🏛️  HOD dashboard
│   ├── student.html             ← 🎒 Student dashboard
│   └── teacher.html             ← 📚 Teacher dashboard
│
├── images/                      ← 🖼️  Project images/assets
└── .vscode/
    └── settings.json            ← ⚙️  VS Code workspace settings
```

---

## 👥 Roles & Access Levels

### 🛡️ Admin — Full System Access

The Admin has complete control over the entire system.

| Feature | Description |
|---------|-------------|
| **Dashboard** | Live stats: total events, pending approvals, conflicts, users |
| **Pending Event Approvals** | Review all HOD event requests with conflict warnings |
| **All Events** | Search and filter by branch, status, date, category |
| **Conflict Detector** | Automatically detects venue/date scheduling overlaps |
| **Suggest Alternate Date** | Send a new date + venue suggestion to the HOD |
| **Approve / Reject Events** | With optional notes to the HOD |
| **Venue Management** | Real-time availability of all 5 college venues |
| **User Management** | Approve new registrations, deactivate users |
| **Analytics** | Bar charts — events by branch, venue, category, approval rate |
| **Notifications** | Activity log for all system events |

---

### 🏛️ HOD (Head of Department)

HODs manage their department's event requests.

| Feature | Description |
|---------|-------------|
| **Dashboard** | Branch-level stats and venue availability today |
| **Request Event** | Submit event with date, venue, and details — live conflict preview shown |
| **My Events** | Track all submitted events and their approval status |
| **Admin Suggestions** | View admin's suggested date/venue and accept or decline |
| **Coordinator Requests** | Approve or reject student coordinator applications |
| **All College Events** | View all approved events across departments |
| **Notifications** | Alerts for approvals, rejections, and date suggestions |

---

### 🎒 Student

Students can browse all events and apply as coordinators.

| Feature | Description |
|---------|-------------|
| **Home** | Featured upcoming events and personal quick stats |
| **Upcoming Events** | Filter by branch/category — apply as coordinator button |
| **Past Events** | Browse all completed events |
| **All Events** | Table view with full details and apply option |
| **My Applications** | Track coordinator application status (Pending / Approved / Rejected) |
| **Event Detail Modal** | Full information with coordinator apply option |
| **Notifications** | Updates on application status |

---

### 📚 Teacher

Teachers have read-only access focused on their branch.

| Feature | Description |
|---------|-------------|
| **Dashboard** | Branch events, other-branch events, today's schedule, category chart |
| **My Branch Events** | All events organized by the teacher's department |
| **All College Events** | Full table with **organizing branch** and **organiser name** highlighted |
| **Venue Schedule** | Per-venue booking list showing which branch organized each event |
| **Notifications** | System alerts |

---

## 🌐 Core System Workflows

### 1. Event Approval Lifecycle
```
HOD submits event request
        ↓
Admin sees request (status: PENDING)
        ↓
   ┌────┴────┐
   ▼         ▼
APPROVE    SUGGEST NEW DATE
   ↓              ↓
Event LIVE    HOD reviews suggestion
Visible to         ↓
all users     Accept → Event APPROVED
              Decline → Stays PENDING
   ↓
REJECT → HOD gets notification with reason
```

### 2. Conflict Detection
```
HOD submits request for Venue X on Date Y
         ↓
Admin opens Pending Events
         ↓
Conflict badge appears automatically (⚠️ red pulse)
         ↓
Conflict Detector page lists ALL overlapping events
         ↓
Admin can Suggest Date / Reject either conflicting event
```

### 3. Student Coordinator Application
```
Student browses Upcoming Events
         ↓
Clicks "Apply as Coordinator"
         ↓
Enters motivation message and submits
         ↓
HOD receives notification
         ↓
HOD approves or rejects via Coordinator Requests page
         ↓
Student sees result in "My Applications"
```

### 4. New Member Registration
```
Go to index.html → Click "Register here"
         ↓
Select Role (HOD / Student / Teacher)
         ↓
Fill in required fields (role-specific form)
         ↓
Account created (status: PENDING APPROVAL)
         ↓
Admin sees new user in User Management → Pending tab
         ↓
Admin clicks "Approve" → User can now log in
```

---

## 🏛️ College Venues (Pre-loaded)

| ID | Venue Name        | Capacity | Description                          |
|----|-------------------|----------|--------------------------------------|
| V1 | Main Auditorium   | 800      | Main hall with stage & AV system     |
| V2 | Seminar Hall A    | 200      | AC seminar hall, ground floor        |
| V3 | Seminar Hall B    | 200      | AC seminar hall, first floor         |
| V4 | Open Ground       | 2,000    | Outdoor sports & cultural ground     |
| V5 | Conference Room   | 50       | Board room with projector            |

---

## 🏫 Departments Supported

```
Computer Science  |  Information Technology  |  Electronics
Mechanical        |  Civil                   |  Electrical
MBA               |  MCA
```

---

## 🗄️ Database Design (localStorage)

All data is stored in the browser's `localStorage` using the following keys:

| Key | Content |
|-----|---------|
| `edu_admins` | Admin user records |
| `edu_hods` | HOD user records |
| `edu_students` | Student user records |
| `edu_teachers` | Teacher user records |
| `edu_events` | All event records |
| `edu_venues` | Venue definitions |
| `edu_coord_requests` | Student coordinator applications |
| `edu_notifications` | System notification log |
| `edu_current_user` | Active logged-in session |

### Event Object Structure
```json
{
  "id": "EVT001",
  "title": "Annual Technical Symposium",
  "description": "...",
  "date": "2026-04-03",
  "endDate": "2026-04-03",
  "venueId": "V1",
  "venueName": "Main Auditorium",
  "branch": "Computer Science",
  "organizer": "Dr. Rajesh Kumar",
  "hodId": "HOD001",
  "status": "approved",
  "category": "Technical",
  "expectedAttendees": 500,
  "createdAt": "2026-03-27T...",
  "adminNote": "",
  "suggestedDate": null,
  "suggestedVenueId": null
}
```

---

## 🎨 Design System

| Attribute | Value |
|-----------|-------|
| **Theme** | Dark mode (deep navy `#0a0d1a`) |
| **Font** | Inter (Google Fonts) |
| **Admin Color** | Gold `#f59e0b` |
| **HOD Color** | Purple `#8b5cf6` |
| **Student Color** | Green `#10b981` |
| **Teacher Color** | Blue `#3b82f6` |
| **Card Style** | Glassmorphism with `backdrop-filter: blur` |
| **Animations** | Floating particles, fade-in cards, hover lifts, pulse alerts |
| **Layout** | Fixed sidebar + scrollable main content |
| **Responsive** | Sidebar auto-collapses on smaller screens |

---

## ✅ Core Requirements Checklist (P-04)

| Requirement | Status |
|-------------|--------|
| Role-Based Access (Admin, HOD, Student) | ✅ Done |
| Teacher access (bonus) | ✅ Done |
| HOD Event Request System | ✅ Done |
| Admin Approval Workflow | ✅ Done |
| Venue Management (5 venues) | ✅ Done |
| Real-time Conflict Detection | ✅ Done |
| Conflict Resolution (suggest date / reject) | ✅ Done |
| Student Event Dashboard (past & future) | ✅ Done |
| Student Coordinator Registration | ✅ Done |
| Event Filtering (date / branch / category) | ✅ Done |
| Notification System | ✅ Done |
| HOD accept/decline admin suggestions | ✅ Done |
| Only registered users can access | ✅ Done |
| Admin user approval workflow | ✅ Done |
| Analytics dashboard | ✅ Done |

---

## 🔒 Security Notes

- Only users with `approved: true` in the database can log in
- New registrations require **Admin approval** before login is possible
- Deactivated (`active: false`) accounts cannot log in
- Each page verifies the session and role before rendering — unauthorized users are redirected to the login page

---

## 🔄 Resetting the Application

To start fresh (clear all data and re-seed defaults):

1. Open **browser DevTools** → `Application` tab → `Storage` → `localStorage`
2. Delete all keys starting with `edu_`
3. Refresh the page — demo data is automatically re-seeded

---

## 👨‍💻 Development Notes

- **No build tools** required — pure HTML/CSS/JS
- **No dependencies** — no npm, no frameworks, no CDN packages (except Google Fonts)
- **No backend** — localStorage simulates a 3-table database
- **Portable** — works offline, just open `index.html`
- To extend with a real backend, replace `js/db.js` methods (get/set/login/register) with `fetch()` API calls

---

## 📄 License

This project was developed as part of **Lab Assignment P-04** for the  
**Artificial Intelligence Applications Lab**.

---

*Built with ❤️ using HTML · CSS · JavaScript*
#   2 0 _ W E B _ T E J A X  
 