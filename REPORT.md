# EDUMON Application — Coursework Report

**Module:** CM3035 Advanced Web Development
**Deliverable:** Final Coursework (50% of module)

---

## 1. Introduction & Requirements Overview

This report documents the design, implementation and testing of a Django-based
EDUMON platform built for the CM3035 Advanced Web Development final
coursework. The brief required a working web application that lets teachers
create and manage courses while students discover, enrol on and engage with
them, built using a conventional Django request/response application, a
Django REST Framework (DRF) API exposing user data, and at least one
real-time module built on Django Channels and WebSockets.

The application satisfies every functional requirement in the brief (R1a
through R1l), the technique requirements around models, forms, the REST
framework, URL routing and testing (R2a–R2e), an appropriately normalised
relational schema (R3), a REST interface for user data (R4), and server-side
unit tests (R5). Beyond the required scope, the project also implements two
of the rubric's bonus items: interactive Swagger/OpenAPI documentation via
`drf-spectacular`, and an advanced technique that pushes live notification
events to a user's browser over the same WebSocket channel layer used for
chat.

The system recognises three roles — Student, Teacher and Admin — enforced
through a `role` field on a custom user model, with every view and API
endpoint checking that role (or object ownership) before allowing an action.
Students can register, browse and enrol on courses, leave feedback, post
status updates to a shared home-page feed, and chat in real time. Teachers
can do everything a student can, plus create and manage courses, upload
course materials, search the user directory, view and block enrolled
students, and receive live notifications when a student enrols. Admins have
full Django admin access for record management.

The remainder of this report explains the architectural decisions behind the
app layout, walks through the data model and why it is shaped the way it is,
maps every brief requirement to the code that satisfies it, explains the
REST API and WebSocket design, describes the testing strategy, offers a
critical evaluation of the finished system, and closes with run instructions.

---

## 2. Architecture & App Breakdown

The project is split into five focused Django apps plus a `config` project
package, so that each app owns a single area of responsibility and the code
inside it stays small enough to navigate at a glance:

- **`config`** — the project package holding `settings.py`, the root
  `urls.py`, and the WSGI/ASGI entry points. `asgi.py` is where the HTTP and
  WebSocket protocols diverge: HTTP requests go through the standard Django
  application, while WebSocket connections are wrapped in Channels'
  `AuthMiddlewareStack` (so `scope['user']` is populated from the session
  cookie) and routed through a combined `URLRouter` built from the chat app's
  and notifications app's routing tables.
- **`accounts`** — the custom user model, registration/login/logout,
  the home page (profile + status feed), viewing another user's profile,
  and the teacher-only user search. This app owns `CustomUser` because
  `AUTH_USER_MODEL` must point somewhere from the very first migration, and
  putting it anywhere else would create a circular dependency with every
  other app that references it.
- **`courses`** — `Course`, `Enrolment`, `Feedback` and `CourseMaterial`
  models, the views for creating courses, browsing/enrolling, uploading
  materials, leaving feedback, and the teacher's block/unblock student
  screen. It also owns the `courses/signals.py` module that fires
  notifications on enrolment and new material, and the `load_demo`
  management command that seeds the whole database.
- **`chat`** — `ChatRoom` and `Message` models, the `ChatConsumer`
  (`AsyncWebsocketConsumer`), its WebSocket routing table, and the views for
  listing/starting/viewing chat rooms.
- **`notifications`** — the `Notification` model, the list/mark-read views,
  a context processor that exposes the unread count to every template (for
  the navbar badge), and the `NotificationConsumer` + `push_notification`
  helper that implement the live-push advanced technique.
- **`api`** — has no models or views of its own; it exists purely to wire
  together the `ViewSet`s defined in `accounts/api.py` and `courses/api.py`
  via a single DRF `DefaultRouter`, and to expose the `drf-spectacular`
  schema and Swagger UI endpoints. Keeping the router assembly separate from
  the ViewSets themselves means the URL surface for the whole API is visible
  in one file (`api/urls.py`) without needing to open every app.

Within each app, code is further split by concern rather than left in a
single `views.py`: `models.py` for schema, `forms.py` for server-side
validation on the HTML views, `serializers.py` and `api.py` for the DRF
layer, `permissions.py` for reusable permission classes, and `signals.py`
where an app needs to react to another app's model changes. This
organisation directly satisfies the C1 (files split appropriately) and C4
(functions with a clear, limited purpose) code-style guidelines, and made it
straightforward to test each layer independently — model tests don't need to
go through a view, and permission logic can be exercised via `APITestCase`
without touching the HTML templates at all.

Templates live in a single top-level `templates/` directory (rather than
inside each app) with one subdirectory per app, extending a shared
`base.html` that renders the navbar, flash messages, and the two WebSocket
`<script>` blocks (chat's inline in `room_detail.html`, notifications'
global in `base.html`). Static assets are served via Bootstrap's CDN build
during development to keep the repository free of a vendored CSS framework.

---

## 3. Data Model & Normalisation

The schema (see `courses/models.py`, `accounts/models.py`, `chat/models.py`
and `notifications/models.py`) is a fairly standard normalised relational
design built around nine models:

| Model | Purpose | Key relationships |
|---|---|---|
| `CustomUser` | Extends `AbstractUser` with `role`, `real_name`, `photo`, `bio` | 1–N `StatusUpdate`; M2N `Course` via `Enrolment` |
| `StatusUpdate` | A short post on a user's home-page feed | N–1 `CustomUser` |
| `Course` | A course owned by a teacher | N–1 teacher; M2N students via `Enrolment` |
| `Enrolment` | Through-table linking a student to a course | N–1 student, N–1 course |
| `Feedback` | A rating + comment a student leaves once per course | N–1 `Course`, N–1 student |
| `CourseMaterial` | A file a teacher uploads to a course | N–1 `Course` |
| `ChatRoom` | A named chat room | M2N `CustomUser` (participants) |
| `Message` | A single persisted chat message | N–1 `ChatRoom`, N–1 sender |
| `Notification` | An in-app/live notification | N–1 recipient |

The most consequential design decision was subclassing `AbstractUser` into
a single `CustomUser` model with a `role` `TextChoices` field, rather than
using separate `Student` and `Teacher` proxy models or Django's group/
permission system. A single table keeps every foreign key in the rest of the
schema pointing at one place (`settings.AUTH_USER_MODEL`), keeps role checks
to a single `is_teacher()`/`is_student()` method pair, and avoids the
multi-table inheritance overhead of a proxy-model approach. The trade-off is
that role-specific fields (there are none needed here beyond the shared
profile fields) would have to live on the same table for both roles, but the
brief's roles are close enough in shape that this was not a real limitation.
`AUTH_USER_MODEL` was set in `config/settings.py` before the first migration
was generated, since Django cannot cleanly swap the user model afterwards
without a manual data migration.

The second consequential decision was making `Enrolment` an explicit
through-model on the `Course.students` M2M field, rather than a bare
`ManyToManyField`. A plain M2M field only records the fact of a relationship;
it cannot carry `enrolled_at` or `is_blocked`. Since R1h requires teachers to
be able to block or remove a student from a course, and R1k requires a
notification the moment a student enrols, the through-model gives both an
explicit row to flag as blocked and an explicit `post_save` signal to hook
into — a plain M2M's `m2m_changed` signal is harder to reason about because
it fires for both `add` and `remove` in the same handler and doesn't expose
a natural "block" flag. `Enrolment` also carries a `unique_together` on
`(student, course)` to enforce third normal form: a student cannot be
enrolled on the same course twice, so `enrolled_at` and `is_blocked` are
functionally dependent on the (student, course) pair as a whole rather than
risking duplicate, potentially inconsistent rows.

`Feedback` similarly enforces `unique_together` on `(course, student)` so a
student leaves at most one rating per course — this reflects the real-world
constraint the brief implies ("leave course feedback") without needing
application-level de-duplication logic scattered across views and the API.

The chat schema deliberately separates `ChatRoom` (an M2N of participants,
addressed by a URL-safe `name`) from `Message` (an immutable, append-only
log referencing a room and a sender). This keeps the WebSocket consumer's
job simple — join a group, append rows, broadcast — and lets both 1:1 direct
messages and, if the brief were extended, group chat rooms be modelled with
the same two tables: a direct message is just a `ChatRoom` with exactly two
participants and a deterministic slug (`dm-<user1>-<user2>`, alphabetically
sorted so the same two users always land on the same room regardless of who
starts the conversation).

`Notification` is intentionally generic — a `recipient`, a free-text `verb`,
an optional `target` reference string, and an `is_read` flag — rather than
polymorphic subclasses per notification type. Given only two notification
triggers exist in this project (enrolment and new material), a single table
with a human-readable `verb` was simpler to query, template and test than a
`ContentType`-based generic foreign key, at the cost of `target` being an
opaque string (`"course:<id>"`) rather than a queryable relation. This was a
deliberate scope trade-off explained further in the critical evaluation.

---

## 4. Feature Walkthrough (Requirements Traceability)

| Req | Requirement | Implementation |
|---|---|---|
| R1a | Users create accounts | `accounts.forms.RegistrationForm` (a `UserCreationForm` subclass with an email-uniqueness validator) + `accounts.views.register` |
| R1b | Log in / log out | Django's built-in `LoginView`/`LogoutView`, subclassed only to point at project templates |
| R1c | Teachers search students & teachers | `accounts.views.search` (web, teacher-only via `PermissionDenied`) and `UserViewSet.list` (API, gated by the `IsTeacher` permission class) |
| R1d | Teachers add courses | `courses.views.course_create` + `CourseForm`, gated by `_require_teacher` |
| R1e | Students enrol on a course | `Enrolment` M2M through-table; `courses.views.enrol` (web) and `CourseViewSet.enrol` (API custom action) |
| R1f | Students leave course feedback | `Feedback` model + `FeedbackForm`; `courses.views.add_feedback` and `CourseViewSet.feedback`, both requiring an active (non-blocked) enrolment |
| R1g | Users chat in real time | `chat` app — `ChatConsumer` (`AsyncWebsocketConsumer`) over a Redis-backed channel layer |
| R1h | Teachers remove/block students | `Enrolment.is_blocked` + `courses.views.toggle_block_student`, restricted to the owning teacher |
| R1i | Users add status updates | `StatusUpdate` model + form, posted from the home page (`accounts.views.home`) |
| R1j | Teachers add course files | `CourseMaterial` (`FileField`) + `courses.views.upload_material` |
| R1k | Teacher notified on enrolment | `courses.signals.notify_teacher_on_enrolment` (`post_save` on `Enrolment`) |
| R1l | Student notified on new material | `courses.signals.notify_students_on_new_material` (`post_save` on `CourseMaterial`), pushed live via WebSocket |

Every view above enforces its permission check server-side (not just by
hiding a button in the template), and each has at least one test asserting
that the wrong role or the wrong user receives a `403`/`404` rather than
succeeding — this was a deliberate priority given how easy it is to get
permission checks half-right and have them look correct in the browser while
being bypassable via a direct POST.

**Status updates and the home page (R1i).** The home page (`accounts/home.html`)
doubles as both "my profile" and "someone else's profile" depending on
whether the URL is `/`(own) or `/user/<username>/` (someone else's); the view
builds the same context dictionary for both cases and the template only
shows the "post a status" form when `is_own_profile` is true. This avoided
writing two near-duplicate templates.

**Blocking (R1h).** Blocking does not remove the `Enrolment` row — it flips
`is_blocked`. This preserves the enrolment history (and any feedback already
left) while immediately cutting the student off from materials and from
leaving further feedback, checked in `course_detail` and `add_feedback`
respectively. Unblocking is the same action toggled the other way, so a
teacher can reverse a mistaken block without the student having to
re-enrol.

**Notifications (R1k, R1l).** Both signals live in `courses/signals.py`
rather than in view code, so a `Notification` is created no matter which
code path triggers the underlying model save (the web view, the API, or the
`load_demo` seed command all fire the same signal). `courses/apps.py`
imports the signal module in `ready()`. Material notifications loop over the
currently enrolled, non-blocked students individually (rather than
`bulk_create`) specifically so each `Notification.objects.create()` call can
be paired with a live `push_notification()` call — `bulk_create` does not
run `post_save`-style hooks per row, which would have silently broken the
live-push bonus feature for materials.

---

## 5. REST API & WebSocket Design

### REST API (R2c, R4)

The API is built with Django REST Framework `ModelViewSet`s registered on a
single `DefaultRouter` in `api/urls.py`:

| Endpoint | Methods | Notes |
|---|---|---|
| `/api/users/` | GET | Teacher-only listing (`IsTeacher`), satisfies R1c over the API |
| `/api/users/{id}/` | GET, PUT, PATCH | Any authenticated user can retrieve; only the owner can update (`IsOwnerOrReadOnly`) |
| `/api/courses/` | GET, POST | Any authenticated user can list; only teachers can create (`IsTeacherOrReadOnly`) |
| `/api/courses/{id}/` | GET, PUT, PATCH, DELETE | Only the owning teacher can update/delete (`IsCourseOwnerOrReadOnly`) |
| `/api/courses/{id}/enrol/` | POST | Custom `@action`; students only, idempotent (`get_or_create`) |
| `/api/courses/{id}/feedback/` | GET, POST | GET is open to any authenticated user; POST requires an active enrolment |
| `/api/statuses/` | GET, POST | Creates a `StatusUpdate` owned by the requesting user |
| `/api/schema/swagger-ui/` | GET | Interactive Swagger UI via `drf-spectacular` |

Permission classes are deliberately small and composable
(`IsTeacher`, `IsOwnerOrReadOnly`, `IsTeacherOrReadOnly`,
`IsCourseOwnerOrReadOnly`) rather than one large conditional block per
ViewSet, and each `ViewSet` overrides `get_permissions()` to vary the
classes by action rather than applying one fixed set — this was necessary
because, for example, `CourseViewSet.enrol` must allow a student (a
non-owner) to POST, while `CourseViewSet.update` must forbid every user
except the owning teacher from doing the same HTTP verb on a different
route. Session authentication is used throughout (`DEFAULT_AUTHENTICATION_CLASSES`
in `settings.py`), which is sufficient for a browsable API used from the same
site session as the HTML views; a token or JWT scheme was not added since
nothing in the brief calls for a separate API-only client.

Pagination (`PageNumberPagination`, page size 20) and `django-filter`
(`DjangoFilterBackend`, filtering courses by `teacher`) are enabled globally
via `REST_FRAMEWORK` settings, and `drf-spectacular` generates the OpenAPI
schema directly from the ViewSets and serializers with no separate schema
file to keep in sync.

### WebSockets (R1g + advanced technique)

Two independent WebSocket routes are mounted in `config/asgi.py`, both
behind `AuthMiddlewareStack` so `scope['user']` reflects the browser's
session cookie:

- **`ws/chat/<room_name>/` → `ChatConsumer`.** On connect, the consumer
  looks up (or creates) the named `ChatRoom`. If the room already existed,
  the connecting user must already be a participant or the connection is
  closed immediately — this stops anyone from joining an existing direct
  message by guessing its slug. On `receive`, the JSON payload's message is
  persisted as a `Message` row and broadcast to every socket in the room's
  channel-layer group via `channel_layer.group_send`.
- **`ws/notifications/` → `NotificationConsumer`.** Each authenticated user
  joins a personal group (`notifications_<user_id>`) on connect. Nothing
  reads from this socket; it exists purely so the server can push to it.

The two routes share the same Redis-backed channel layer
(`channels_redis.core.RedisChannelLayer`, configured from a `REDIS_URL`
environment variable, falling back to Django's in-memory layer when
`CHANNEL_LAYER_BACKEND=memory` is set — used for the test suite so tests
don't require a running Redis instance). Reusing one channel layer for both
chat and live notifications is the "advanced technique" claimed for the
bonus marks: `notifications/utils.py`'s `push_notification()` helper is
called from the same `courses/signals.py` handlers that create the
`Notification` rows, using `async_to_sync(channel_layer.group_send)` from
synchronous signal-handler code, and the browser-side listener is a small
inline script in `base.html` that increments the navbar badge the instant a
push arrives — without a page reload.

### Security Measures (Non-Functional Requirements)

Several security properties are enforced by configuration and code rather
than left implicit. Passwords are never stored in plaintext: `CustomUser`
inherits Django's `AbstractUser`, so account creation always goes through
`create_user()`/`UserCreationForm`, both of which hash passwords with
Django's configurable PBKDF2-based hasher before they touch the database,
and `AUTH_PASSWORD_VALIDATORS` in `settings.py` rejects passwords that are
too short, too common, entirely numeric, or too similar to the user's own
account details. Every state-changing view uses Django's session-based CSRF
protection (`{% csrf_token %}` in every form, `CsrfViewMiddleware` in the
middleware stack); the WebSocket consumers do not need a CSRF token because
they authenticate via the session cookie carried through
`AuthMiddlewareStack`, and a connection is rejected outright if
`scope['user']` is not authenticated. Role-based and object-level permission
checks are enforced entirely server-side — in the HTML views via explicit
`PermissionDenied` raises (never just a hidden button), and in the API via
the composable permission classes described above — so the same protection
holds whether a request comes from the rendered page or a raw HTTP client.
File uploads (`CourseMaterial.file`, `CustomUser.photo`) are handled through
Django's `FileField`/`ImageField`, which write outside any executable path
and never trust the client-supplied filename directly for storage; validating
upload size against `MAX_UPLOAD_SIZE` and restricting file extensions is
flagged in the critical evaluation below as the next hardening step.

---

## 6. Testing Approach

The project has 83 automated tests spread across every app, run with
Django's `TestCase` for models/views/signals and DRF's `APITestCase` for the
REST layer, satisfying R5 and C6. Coverage was built up phase-by-phase
alongside the feature it tests, rather than left for the end, specifically
because unit testing carries 6 rubric points and thin, bolted-on tests are
one of the easiest ways to lose them. The suite is organised as:

- **Model tests** — default values, `__str__` output, uniqueness
  constraints (`Enrolment.unique_together`, `Feedback.unique_together`),
  and ordering (`Meta.ordering` on `StatusUpdate`, `Message`, `Notification`).
- **Form tests** — `RegistrationForm` password-mismatch and duplicate-email
  rejection; `StatusUpdateForm` length limits; `FeedbackForm`/model
  `full_clean()` rating bounds.
- **View tests** — one happy-path test per view plus at least one
  permission-denial test per role boundary (student vs teacher, owner vs
  non-owner, blocked vs active enrolment), asserting the exact status code
  (`302` for login-required redirects, `403` for `PermissionDenied`, `404`
  for "doesn't exist for this user" lookups).
- **Signal tests** — asserting a `Notification` row is created with the
  expected `verb` when an `Enrolment` or `CourseMaterial` is saved, that
  re-saving an existing `Enrolment` does not create a duplicate
  notification, and that a blocked student is excluded from material
  notifications.
- **API tests** (`APITestCase`) — list/create/update/delete across every
  ViewSet, exercising each custom permission class from both sides (the
  user who should succeed and the user who should be forbidden), plus the
  custom `enrol` and `feedback` actions and the Swagger/schema endpoints.
- **Consumer tests** — `chat/tests/test_consumers.py` uses Channels'
  `WebsocketCommunicator` inside an async `TransactionTestCase` to connect
  two simulated users to the same room, send a message from one, and assert
  the other receives it — this is the automated equivalent of the "two
  browsers chatting live" demo and does not require a running Redis
  instance (it uses the in-memory channel layer during tests).

**How to run the tests.** From the `EDUMON/` directory, with the
virtualenv active:

```bash
python manage.py test
```

This runs against Django's in-memory SQLite test database and the channel
layer configured by `CHANNEL_LAYERS` in `settings.py`. If Redis is not
running locally, set `CHANNEL_LAYER_BACKEND=memory` first so Channels falls
back to its in-memory layer instead of trying to reach Redis:

```bash
CHANNEL_LAYER_BACKEND=memory python manage.py test
```

Both configurations were verified during development — the full suite
passes against both the in-memory layer and a real local Redis instance —
so the tests are not accidentally dependent on infrastructure that isn't
actually part of what they claim to verify.

---

## 7. Critical Evaluation

**What worked well.** Splitting each app into `models.py` / `views.py` /
`forms.py` / `serializers.py` / `api.py` / `permissions.py` /
`signals.py` from the start made it easy to keep growing the project phase
by phase without files becoming unmanageable, and made permission logic easy
to unit-test in isolation from HTTP concerns. Reusing a single Redis channel
layer for both chat and live notification push was a small addition on top
of the required chat feature that meaningfully improved the demo (a teacher
sees an enrolment notification pop into their navbar without refreshing)
for very little extra code — `notifications/utils.py` is nineteen lines.
Writing the `ChatConsumer`'s "reject if not already a participant" check
early avoided a real information-leak: an early draft let anyone type a
guessable room-name in the address bar and read someone else's direct
messages, and the accompanying consumer test (`test_non_participant_is_rejected`)
now guards against that regressing.

**What is a genuine limitation.** `Notification.target` is a free-text
string (`"course:<id>"`) rather than a `GenericForeignKey`, which was the
right trade-off for two notification types but would not scale cleanly if a
third or fourth notification trigger were added later — a generic relation
or a small `notification_type` enum with type-specific serializers would be
the natural next step. Similarly, `ChatRoom` only supports the 1:1 direct-
message pattern used by the UI (`start_chat` always builds a deterministic
two-user slug); the model itself supports N participants, but there is no
view for creating or naming an arbitrary group room, which the brief did not
require but a real deployment likely would. Session authentication for the
API is adequate for a browser client sharing the Django session, but would
need to be swapped for token or JWT authentication before any non-browser
client (a mobile app, a third-party integration) could use it.

**What I would change with more time.** The chat UI's WebSocket client is a
small inline `<script>` block rather than a reusable JS module — fine for a
single consumer, but it would not scale to a third real-time feature without
factoring out a small shared "reconnecting socket" helper. I would also add
rate-limiting to the `StatusUpdate` and `Message` creation paths; nothing in
the current implementation stops a user from posting in a tight loop, which
is a reasonable next hardening step before any real deployment. Finally,
`CourseMaterial` currently accepts any file type up to Django's default
upload-size handling; a production version should validate file extensions
and enforce the `MAX_UPLOAD_SIZE` setting already defined (but not yet wired
into a validator) in `config/settings.py`.

**Comparison with the state of the art.** Modern production LMS platforms
(Canvas, Moodle) separate real-time messaging into a dedicated service and
use a message broker (Kafka, or a managed pub/sub) rather than a single
Redis instance backing Django Channels directly; for the scale this
coursework targets, Channels + Redis is the correct, taught-syllabus choice
and avoids introducing infrastructure the brief does not ask for. Likewise,
production systems typically separate "read" and "write" notification
delivery (a durable outbox table plus a delivery worker) so a dropped
WebSocket connection cannot silently lose a notification; here, the
`Notification` row is always persisted first and the live push is a
best-effort addition on top, so a user who is offline when a notification
fires will still see it in `/notifications/` on their next visit — the
degraded case (offline) still meets the R1k/R1l requirement even though the
live-push bonus only fires for connected clients.

---

## 8. Run Instructions

**Operating system used for development:** macOS (Darwin 25.5.0 / macOS
26.5.1, arm64).
**Python version:** 3.12.14.
**Key package versions:** Django 5.0.14, djangorestframework 3.17.2,
channels 4.3.2, channels_redis 4.3.0, daphne 4.2.3, drf-spectacular 0.30.0,
django-filter 25.1, Pillow 12.3.0, redis-py 8.1.0 (full pinned list in
`EDUMON/requirements.txt`).

### 1. Install

```bash
cd EDUMON
python3.12 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

A Redis server is required for real-time chat and live notifications
(install via `brew install redis` on macOS, or run the official Docker
image). Start it before running the app:

```bash
redis-server            # or: brew services start redis
```

### 2. Configure the database and demo data

```bash
python manage.py migrate
python manage.py load_demo      # seeds admin, teachers, students, courses
```

`load_demo` is idempotent — running it a second time detects the existing
`admin` account and does nothing.

### 3. Run the server

Because the project uses Django Channels, run it through Daphne (an ASGI
server) rather than the plain WSGI dev server so WebSocket connections are
handled correctly:

```bash
daphne -p 8000 config.asgi:application
```

(`python manage.py runserver` also works for HTTP-only testing of the
non-chat pages, since Django 5's `runserver` will hand off to Channels'
ASGI handler automatically when `channels` is installed and `daphne` is
listed first in `INSTALLED_APPS`.)

Visit `http://127.0.0.1:8000/`.

### 4. Demo credentials (created by `load_demo`)

| Role | Username | Password |
|---|---|---|
| Admin (superuser) | `admin` | `adminpass123` |
| Teacher | `t_smith` | `teachpass123` |
| Teacher | `t_jones` | `teachpass123` |
| Student | `s_student1` … `s_student5` | `studentpass123` |

Django admin is at `/admin/`, the Swagger API docs are at
`/api/schema/swagger-ui/`.

### 5. Run the tests

```bash
python manage.py test                                   # needs Redis running
CHANNEL_LAYER_BACKEND=memory python manage.py test       # no Redis required
```

### 6. Deployment

Not deployed for this submission; the settings module already reads
`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS` and `REDIS_URL`
from the environment so it is deploy-ready for a platform such as Render,
Fly.io or a small VPS without any code changes — only environment variables,
a production database (PostgreSQL is a drop-in replacement for the SQLite
`DATABASES` entry), and a managed Redis instance would need to be
provisioned.
