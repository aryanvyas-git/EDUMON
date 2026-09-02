# Product Requirements Document — EDUMON Application

**Module:** CM3035 Advanced Web Development · Final Coursework (50% of module)
**Stack:** Django + Django REST Framework + Django Channels (WebSockets)
**Due:** 14 Sep, 2:00 PM BST

---

## 1. Overview

**Product.** A Django-based EDUMON web platform where teachers create and manage courses and students discover, enrol on, and engage with them. The application combines a conventional request/response Django app, a Django REST Framework (DRF) API for user data, and at least one real-time module powered by Django Channels and WebSockets.

**Goal.** Satisfy every functional requirement (R1a–R1l), technique requirement (R2–R5), and code-style guideline (C1–C6) in the brief, while maximising rubric points — including the bonus items (advanced techniques, video presentation, cloud deployment).

---

## 2. Users & Roles

| Role | Can do | Cannot do |
|---|---|---|
| **Student** | Create account, log in/out; browse & enrol on courses; leave course feedback; post status updates to home page; real-time chat; access enrolled course materials | Create courses; search users; block/remove students; access other students' admin records |
| **Teacher** | All account actions; create/manage courses & upload materials; view enrolled-student list; search students & teachers; block/remove students from a course; real-time chat; receive enrolment notifications | Access Django admin (unless also superuser) |
| **Admin (superuser)** | Full Django admin access; manage all records | — |

Role is a field on the custom user model; every view and API endpoint must enforce role-based permissions.

---

## 3. Functional Requirements Traceability

Every brief/rubric requirement mapped to the feature and Django component that satisfies it. Reuse this table as the compliance matrix in the report.

| Req | Requirement | Where implemented |
|---|---|---|
| R1a | Users create accounts | `accounts` app — registration form + `CustomUser` model |
| R1b | Log in / log out | Django auth views + session auth |
| R1c | Teachers search students & teachers | Search view + DRF filter endpoint |
| R1d | Teachers add courses | `courses` app — `Course` model + create view |
| R1e | Students enrol on a course | `Enrolment` model (M2M through-table) |
| R1f | Students leave course feedback | `Feedback` model + form |
| R1g | Users chat in real time | `chat` app — Channels consumer + WebSocket |
| R1h | Teachers remove/block students | `Enrolment.is_blocked` flag + teacher action |
| R1i | Users add status updates | `StatusUpdate` model on home page |
| R1j | Teachers add course files | `CourseMaterial` model (`FileField`) |
| R1k | Teacher notified on enrolment | `Notification` model via Django signals |
| R1l | Student notified on new material | `Notification` via signals + WebSocket push |
| R2 | Models, forms, DRF, routing, tests | Cross-cutting — all apps |
| R3 | Appropriate relational schema | See §6 data model |
| R4 | REST interface for user data | `api` — DRF ViewSets + serializers |
| R5 | Server-side tests | `tests/` in each app + `APITestCase` |

### R2 sub-requirements
- **R2a** correct models & migrations
- **R2b** correct forms, validators & serialisation
- **R2c** correct use of django-rest-framework
- **R2d** correct URL routing
- **R2e** appropriate unit testing

---

## 4. Non-Functional Requirements

- **Reproducibility:** app installs cleanly from `requirements.txt` into a fresh virtualenv; a `load_demo` management command or fixtures seed demo users, courses and enrolments.
- **Security:** password-hashed accounts, CSRF protection, role-based permission checks on every view and API endpoint, file-upload validation.
- **Code quality:** PEP 8 layout, meaningful names, docstrings/comments, modular code split across view/api/serializer files (C1–C6).
- **Testability:** unit tests for models, views, permissions and the API; documented test-run instructions.
- **Real-time:** Redis-backed channel layer; at least one working WebSocket app (chat).

---

## 5. Scope

### In scope (must-have)
All R1–R5 requirements, one WebSocket module, a REST API for user data, unit tests, and the three written/recorded deliverables (report, video, demo data).

### Bonus scope (score-boosting)
- Swagger/OpenAPI docs (`drf-spectacular`) — explicitly rewarded in the rubric.
- One advanced technique beyond taught material — e.g. a frontend framework, live notifications over WebSockets, or a shared whiteboard.
- Cloud deployment (AWS / DigitalOcean / Render) with credentials in the report — up to 7 bonus points.
- Polished video presentation clearly highlighting achievements — up to 5 points.

### Out of scope
Payment processing, mobile-native apps, and production-grade horizontal scaling are not required.

---

## 6. Data Model

Schema covering accounts, courses, the many-to-many enrolment relationship (with a through-table so blocking is possible), feedback, materials, status updates, chat, and notifications.

| Model | Key fields | Relationships |
|---|---|---|
| `CustomUser` | username, email, real_name, photo, role (student/teacher), bio | 1—N `StatusUpdate`; M2N `Course` via `Enrolment` |
| `StatusUpdate` | user FK, content, created_at | N—1 `CustomUser` |
| `Course` | title, description, teacher FK, created_at | N—1 teacher; M2N students |
| `Enrolment` | student FK, course FK, enrolled_at, is_blocked | through-table linking student↔course (R1e/h) |
| `Feedback` | course FK, student FK, rating, comment | N—1 `Course`, N—1 student (R1f) |
| `CourseMaterial` | course FK, title, file, uploaded_at | N—1 `Course` (R1j) |
| `ChatRoom` | name/slug, participants M2M | M2N `CustomUser` |
| `Message` | room FK, sender FK, body, timestamp | N—1 `ChatRoom`, N—1 sender |
| `Notification` | recipient FK, verb, target, is_read, created_at | N—1 `CustomUser` (R1k/l) |

### Key design notes
- **CustomUser over the default:** subclass `AbstractUser` and add a `role` field so student/teacher permissions branch cleanly. **Set `AUTH_USER_MODEL` from the very first migration — changing it later is painful.**
- **Enrolment as an explicit through-model:** gives you `enrolled_at` and `is_blocked`, which R1h (block/remove) and the enrolment notification signal (R1k) both need.
- **Signals for notifications:** `post_save` on `Enrolment` notifies the teacher; `post_save` on `CourseMaterial` notifies enrolled students. Keeps view code clean and satisfies R1k/R1l.

---

## 7. REST API Surface (R4)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/users/` | GET | List users (search students/teachers, R1c) |
| `/api/users/{id}/` | GET/PUT | Retrieve/update own profile |
| `/api/courses/` | GET/POST | List / create courses |
| `/api/courses/{id}/` | GET/PUT/DELETE | Course detail & management |
| `/api/courses/{id}/enrol/` | POST | Student self-enrolment |
| `/api/courses/{id}/feedback/` | GET/POST | Course feedback |
| `/api/statuses/` | GET/POST | Status updates |
| `/api/schema/swagger-ui/` | GET | Interactive API docs (bonus) |

**Auth & permissions:** session auth for the browser; session/token for the API. Enforce per-object permissions (`IsOwnerOrReadOnly`, `IsTeacher`) so a student can never reach teacher-only endpoints.

---

## 8. Real-Time Module (R1g)

Implement a chat consumer with Django Channels.

**Flow:** client opens `ws://…/ws/chat/<room>/` → `ChatConsumer` (`AsyncWebsocketConsumer`) joins a Redis-backed group → messages are broadcast to the group and persisted to the `Message` model.

The video demo must show launching the Redis server and a second browser/user joining a live chat.

**Advanced-technique idea:** reuse the same channel layer to push live `Notification` events (enrolment, new material) to a user's browser — one feature that ticks R1g, R1k, R1l and the "advanced techniques" bonus at once.

---

## 9. Code-Style Guidelines (C1–C6)

- **C1** Code organised into appropriate files (views in `views.py`/`api.py`, models in `models.py`).
- **C2** Appropriate comments for clarity/readability.
- **C3** Clear layout, consistent indenting, PEP 8.
- **C4** Code organised into functions with clear, limited purpose.
- **C5** Meaningful, consistently-named functions, classes and variables.
- **C6** Appropriate tests covering the API.
