# Implementation Guide — EDUMON Application

Companion to `PRD.md`. Build in dependency order. **Each phase must end in a runnable, testable state — commit at every phase boundary.** Requirement tags (R1a, R2c, etc.) refer to `PRD.md`.

---

## Technology Stack

| Layer | Choice | Notes |
|---|---|---|
| Framework | Django 5.x | Course-standard |
| API | Django REST Framework | Required (R2c, R4) |
| API docs | drf-spectacular (Swagger) | Rubric rewards swagger |
| Real-time | Django Channels + Daphne | Required WebSocket support |
| Channel layer | Redis (channels-redis) | Demo must show redis server |
| Async tasks | Celery + Redis (optional) | Taught topic; notifications |
| DB (dev) | SQLite | Zero-config for grading |
| DB (prod) | PostgreSQL | For deployment bonus |
| Frontend | Django templates + Bootstrap | Or SPA — your choice |
| Testing | Django `TestCase` + `APITestCase` | Required (R5, C6) |
| Image handling | Pillow | For user photo / uploads |

---

## Target Project Layout

Split responsibilities across focused apps so views, models, serializers and API code each sit in the right file (satisfies C1).

```
EDUMON/
├── manage.py
├── requirements.txt
├── config/                  # project settings package
│   ├── settings.py          # (or split base/dev/prod)
│   ├── urls.py              # root URL routing (R2d)
│   ├── asgi.py              # Channels/ASGI entrypoint
│   └── wsgi.py
├── accounts/                # CustomUser, auth, profiles, home page
│   ├── models.py            # CustomUser, StatusUpdate
│   ├── views.py             # registration, login, home, search
│   ├── forms.py             # forms + validators (R2b)
│   ├── api.py               # DRF user ViewSets (R4)
│   ├── serializers.py       # DRF serializers (R2b)
│   ├── permissions.py       # IsTeacher / IsOwner
│   └── tests/
├── courses/                 # Course, Enrolment, Feedback, Material
│   ├── models.py
│   ├── views.py / api.py / serializers.py / forms.py
│   ├── signals.py           # enrolment & material notifications (R1k/l)
│   └── tests/
├── chat/                    # WebSocket real-time module (R1g)
│   ├── consumers.py         # AsyncWebsocketConsumer
│   ├── routing.py           # ws/ URL routing
│   └── models.py            # ChatRoom, Message
├── notifications/           # Notification model + delivery
├── templates/  static/  media/
└── fixtures/ or management command  # demo data (D1)
```

---

## Phase 0 — Project Setup `foundation`

1. Create virtualenv; install Django, DRF, channels, channels-redis, daphne, drf-spectacular, Pillow.
2. Start project (`config`) and the `accounts` app. **Set `AUTH_USER_MODEL` before the first migration.**
3. Configure settings: installed apps, DRF, Channels ASGI, Redis channel layer, media/static, templates.
4. Initialise git; freeze `requirements.txt` early and keep it current.

**Done when:** `python manage.py runserver` boots with no migrations pending on an empty custom-user schema.

---

## Phase 1 — Accounts & Auth `R1a, R1b, R2a`

1. `CustomUser` model (role, real_name, photo, bio) + migration.
2. Registration form with validators; login/logout using Django auth views.
3. Home page view showing profile, enrolled courses, deadlines, status updates — discoverable/visible to other users.
4. `StatusUpdate` model + post form (R1i). Write first model/view tests.

**Done when:** a user can register, log in, view their home page, post a status update, and view another user's home page.

---

## Phase 2 — Courses & Enrolment `R1d, R1e, R1f, R1j, R3`

1. `Course`, `Enrolment` (through-model with `is_blocked`), `Feedback`, `CourseMaterial` models + migrations.
2. Teacher: create course, upload materials, view enrolled-student list.
3. Student: browse available courses, self-enrol, leave feedback.
4. Teacher block/remove student action (R1h). Tests for enrolment & permissions.

**Done when:** a teacher creates a course with materials; a student enrols and leaves feedback; a teacher can block a student.

---

## Phase 3 — Search & Notifications `R1c, R1h, R1k, R1l`

1. Teacher search for students/teachers (view + API filter).
2. `Notification` model + signals: notify teacher on enrol (R1k), notify enrolled students on new material (R1l).
3. Notification list/read UI on the home page. Tests for signal firing.

**Done when:** enrolling triggers a teacher notification and adding material triggers student notifications, both visible in the UI.

---

## Phase 4 — REST API `R2c, R4, C6` + swagger bonus

1. Serializers for User, Course, Enrolment, Feedback, StatusUpdate.
2. ViewSets + routers in `api.py`; wire URL routing (R2d).
3. Per-object permission classes; hook up drf-spectacular Swagger UI at `/api/schema/swagger-ui/`.
4. `APITestCase` covering list / create / permission-denied paths (C6).

**Done when:** the documented endpoints in PRD §7 work, enforce permissions, and appear in Swagger.

---

## Phase 5 — Real-Time Chat `R1g`

1. `ChatRoom` + `Message` models; `ChatConsumer` (`AsyncWebsocketConsumer`).
2. `routing.py` ws routes; Redis channel layer; chat template + JS client.
3. Persist messages; verify two users chat live.
4. *(Optional advanced-technique bonus)* push live notifications over the same channel layer.

**Done when:** two logged-in users in separate browsers exchange messages in real time, and messages persist across reloads.

---

## Phase 6 — Testing, Demo Data, Polish `R5, C1–C5, D1`

1. Fill test gaps: models, views, permissions, API, signals. **Unit testing is worth 6 rubric points — aim for meaningful coverage.**
2. `load_demo` management command or fixtures: sample teachers, students, courses, enrolments.
3. PEP 8 pass, docstrings/comments, tidy naming, remove dead code (C1–C5).
4. Verify clean install from `requirements.txt` in a fresh venv.

**Done when:** `python manage.py test` passes; a fresh clone installs and runs with seeded demo data.

---

## Phase 7 — Deliverables `D1–D4` + bonuses

1. Report (4000–6000 words): design rationale, requirements mapping, critical evaluation, run/test/login instructions, OS & Python version, packages+versions.
2. Record ≤10-min mp4 video hitting every required demo beat (see below).
3. *(Bonus)* Deploy to AWS/DigitalOcean/Render; add live URL + credentials to report.
4. Zip D1, export report PDF, upload video / unlisted YouTube link.

---

## Video Demo Checklist (D3) — must show, in order

- [ ] Install the app from `requirements.txt`.
- [ ] Talk through database design and normalisation.
- [ ] Run the unit tests (show them passing).
- [ ] Launch the app and log in — show a course, feedback and status updates.
- [ ] Launch the Redis server, open a second browser, log in a second user, start a live chat.
- [ ] Clearly narrate achievements throughout. Under 10 minutes, mp4, **video unlisted**.

---

## Report Structure (D2, 4000–6000 words)

1. Introduction & requirements overview.
2. Architecture & app breakdown (why the code is arranged as it is).
3. Data model & normalisation.
4. Feature walkthrough mapped to R1a–R1l (reuse the PRD §3 matrix).
5. REST API & WebSocket design.
6. Testing approach + how to run the tests.
7. Critical evaluation: what worked, what to improve, what you'd change.
8. Run instructions: unzip, install, packages+versions, OS, Python version, admin + teacher/student credentials, deployment URL (if any).

---

## Rubric Coverage Map (70 points)

| Rubric criterion | Marks | Covered by |
|---|---|---|
| App loads via valid requirements.txt | 4 | Phase 0/6 |
| Implements all specified functionality | 5 | Phases 1–5 |
| Database/model design appropriate | 3 | PRD §6 |
| Frontend design appropriate | 4 | Phase 1–5 templates |
| Uses Django topics 1–10 incl. swagger | 4 | Phase 4 |
| Unit testing included | 6 | Phase 6 |
| Clean code, syntax, comments | 3 | C2–C3 |
| Code functional / reproducible | 3 | Phase 6 |
| Modular & well organised | 4 | C1, C4, layout |
| Advanced techniques used | 5 | Phase 5 bonus |
| Report clearly written | 3 | Phase 7 |
| Report explains requirements met | 3 | PRD §3 matrix |
| Best-practice Django/DRF/sockets | 4 | Phases 4–5 |
| Critical evaluation vs state of the art | 4 | Report §7 |
| Run info: OS, Python, credentials | 3 | Report §8 |
| Video presentation of achievements | 5 | Video checklist |
| Deployment bonus (AWS/DO/etc.) | 7 | Phase 7 bonus |

---

## Common Point-Losers to Avoid

- Changing `AUTH_USER_MODEL` after migrations exist — start with `CustomUser`.
- Thin or missing tests — testing is 6 rubric points; don't leave it to the end.
- `requirements.txt` that doesn't reproduce the environment — verify in a clean venv.
- Forgetting run/login credentials and OS/Python version in the report (3 easy points).
- Video over 10 minutes, or not showing Redis + two-user chat.
- Leaving the demo video public instead of unlisted.
