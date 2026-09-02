# DESIGN.md — EDUMON Application Visual System

This document defines the frontend design language for the EDUMON app. It is derived from two reference templates: a **dashboard/app UI** (clean SaaS, charcoal sidebar, indigo primary, soft cards) and a **marketing/landing UI** (playful, sky-blue, green/yellow accents, bold display type).

**Rule of thumb:** authenticated *app* screens (dashboard, courses, chat, profile, admin) follow the **App Theme**. Public *marketing/auth* screens (landing, login, register) follow the **Marketing Theme**. Both share the same token palette and font stack so the app feels like one product.

---

## 1. Design Principles

1. **Calm app, warm front door.** The working area is neutral and low-noise; the landing pages are bright and inviting.
2. **Soft, rounded, elevated.** Everything is on rounded cards with gentle shadows on a light-grey canvas — never hard borders on white.
3. **One primary, two accents.** Indigo/blue drives actions. Green and yellow are used sparingly for highlights, illustrations and marketing blocks.
4. **Generous whitespace.** Cards breathe; content is never edge-to-edge.
5. **Status is always a pill.** Progress, completion and roles are shown as pill badges and progress bars, never as raw text.
6. **Illustrations over stock photos** in the app; friendly photo + illustration mix on the landing page.

---

## 2. Color Tokens

Define these as CSS custom properties on `:root`. Never hardcode hex values in components.

```css
:root {
  /* ---- Brand / Primary (indigo-blue) ---- */
  --color-primary:        #2F5BEA;   /* primary buttons, active nav, links */
  --color-primary-hover:  #2447C4;
  --color-primary-soft:   #E8EDFD;   /* tinted button bg, active-nav bg on light */
  --color-primary-ring:   #C4D2FA;   /* focus rings */

  /* ---- Accents ---- */
  --color-accent-green:   #34C759;   /* success, "completed", marketing green card */
  --color-green-soft:     #E4F8EA;
  --color-accent-yellow:  #FBD34D;   /* marketing CTA card, highlights */
  --color-yellow-soft:    #FEF3CF;
  --color-accent-pink:    #EC4899;   /* secondary progress bar (reading) */
  --color-accent-purple:  #8B5CF6;   /* primary progress bar (math) */
  --color-sky:            #4FC3F7;   /* marketing hero background wash */
  --color-sky-soft:       #E3F5FD;

  /* ---- Sidebar (dark) ---- */
  --color-sidebar-bg:     #14161A;   /* near-black charcoal */
  --color-sidebar-fg:     #E7E9EE;   /* default nav label */
  --color-sidebar-muted:  #9AA0AB;   /* inactive icon/label */
  --color-sidebar-active-bg: var(--color-primary);
  --color-sidebar-active-fg: #FFFFFF;

  /* ---- Surfaces ---- */
  --color-canvas:         #F6F7FB;   /* app background behind cards */
  --color-surface:        #FFFFFF;   /* card background */
  --color-surface-alt:    #FBFCFE;   /* subtle inner panels */

  /* ---- Text ---- */
  --color-text:           #1A1D23;   /* headings / primary text */
  --color-text-secondary: #5B6270;   /* body / labels */
  --color-text-muted:     #9096A2;   /* captions, meta, "Time: 15 minutes" */
  --color-text-invert:    #FFFFFF;

  /* ---- Status ---- */
  --color-success:        #16A34A;
  --color-success-soft:   #DCFCE7;
  --color-warning:        #D97706;   /* "In-Progress" amber */
  --color-warning-soft:   #FEF3C7;
  --color-neutral:        #6B7280;   /* "Not Started" grey */
  --color-neutral-soft:   #EEF0F3;
  --color-danger:         #DC2626;
  --color-danger-soft:    #FEE2E2;

  /* ---- Lines ---- */
  --color-border:         #E9EBF0;   /* hairline dividers, card edges */
  --color-border-strong:  #D6DAE2;
}
```

### Usage map
| Element | Token |
|---|---|
| Primary button, active nav item, links | `--color-primary` |
| Sidebar background | `--color-sidebar-bg` |
| App background (behind cards) | `--color-canvas` |
| Card background | `--color-surface` |
| "Completed" badge | `--color-success` on `--color-success-soft` |
| "In-Progress" badge | `--color-warning` on `--color-warning-soft` |
| "Not Started" badge | `--color-neutral` on `--color-neutral-soft` |
| Role badge (e.g. "Grade 2" / "Teacher") | `--color-primary` on `--color-primary-soft` |
| Math-style progress bar | `--color-accent-purple` |
| Reading-style progress bar | `--color-accent-pink` |
| Marketing hero wash | `--color-sky` |
| Marketing highlight card | `--color-accent-yellow` / `--color-accent-green` |

---

## 3. Typography

Both references use a clean geometric/grotesque sans. Use **Inter** as the primary UI face (free, web-safe via Google Fonts) with a heavier display weight on the marketing hero.

```css
:root {
  --font-sans: "Inter", -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-display: "Inter", sans-serif; /* use weight 800 for hero */
}
```

- Load Inter weights: 400, 500, 600, 700, 800.
- **Marketing hero** ("Learn. Grow. Succeed") uses weight **800**, very tight line-height (~1.0), large negative letter-spacing (~-0.02em). Optional: a hand-written accent font (e.g. *Caveat*) for small script labels like "What Industry We Serve!".

### Type Scale
| Token | Size / line-height | Weight | Use |
|---|---|---|---|
| `display` | 56px / 1.0 | 800 | Marketing hero headline |
| `h1` | 30px / 1.2 | 700 | Page title ("Dashboard") |
| `h2` | 22px / 1.3 | 700 | Section title ("Today's Activity") |
| `h3` | 17px / 1.4 | 600 | Card title ("Math", "Reading") |
| `body` | 15px / 1.55 | 400 | Default text |
| `body-sm` | 13px / 1.5 | 400 | Secondary text |
| `label` | 13px / 1.4 | 600 | Nav items, buttons |
| `caption` | 12px / 1.4 | 500 | Meta ("Time: 15 minutes", "Lesson-1") |
| `stat` | 34px / 1.1 | 700 | Big KPI numbers ("80 %", "1h 39m") |

---

## 4. Spacing, Radius, Shadow, Layout

```css
:root {
  /* spacing scale (4px base) */
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
  --space-5: 20px; --space-6: 24px; --space-8: 32px; --space-10: 40px;
  --space-12: 48px;

  /* radius — everything is generously rounded */
  --radius-sm:  8px;    /* badges, small inputs */
  --radius-md:  12px;   /* buttons, list rows */
  --radius-lg:  16px;   /* cards */
  --radius-xl:  20px;   /* KPI cards, large panels */
  --radius-2xl: 28px;   /* marketing blocks */
  --radius-pill: 999px; /* status pills, avatars */

  /* shadows — soft, diffuse, low-opacity; NO hard borders on cards */
  --shadow-xs: 0 1px 2px rgba(20,22,26,0.04);
  --shadow-sm: 0 2px 8px rgba(20,22,26,0.05);
  --shadow-md: 0 6px 20px rgba(20,22,26,0.07);
  --shadow-lg: 0 12px 32px rgba(20,22,26,0.10);

  /* layout */
  --sidebar-width: 248px;
  --content-max: 1200px;
  --header-height: 68px;
}
```

**App shell layout:**
- Fixed dark sidebar `--sidebar-width` on the left, full height.
- Main area on `--color-canvas`, padded `--space-8`, content capped at `--content-max`.
- Cards sit on the canvas with `--radius-lg`/`--radius-xl` and `--shadow-sm`/`--shadow-md`. **Cards have no visible border — separation comes from shadow + background contrast.**

---

## 5. Core Components

### 5.1 Sidebar (App Theme)
- Background `--color-sidebar-bg`, full viewport height, `--sidebar-width` wide.
- Top: logo mark (rounded-square gradient icon) + wordmark in white, `h3` weight, with a collapse toggle on the right.
- Nav items: icon + label, `label` type, `--color-sidebar-muted` by default.
  - **Active item:** solid `--color-primary` pill (`--radius-md`), white text/icon, full-width minus side padding. Only one active at a time.
  - Hover (inactive): text brightens to `--color-sidebar-fg`, subtle `rgba(255,255,255,0.05)` background.
- Bottom cluster (pushed down): Settings, Help, Log out — same style, muted.
- Icons: line icons (Lucide/Feather), 20px, 1.75 stroke.

### 5.2 KPI / Stat Card
- White surface, `--radius-xl`, `--shadow-sm`, padding `--space-6`.
- Big number in `stat` type on the left, small `body-sm` label under it in `--color-text-secondary`.
- Decorative illustration/icon on the right (~64–80px).
- Used for "Student Progress 80%", "Total Activity 80%", "Total Time 1h 39m".

### 5.3 Course/Subject Card
- White surface, `--radius-lg`, `--shadow-sm`, padding `--space-6`.
- Header row: title (`h3`) + a role/grade pill (`--color-primary` on `--color-primary-soft`), and a right-aligned outline button ("Next Grade").
- Sub-label under title in `--color-text-muted` ("Basic Math").
- A short bulleted topic list in `body-sm`.
- **Progress bar** at the bottom: rounded track (`--radius-pill`, `--color-neutral-soft` bg) with a colored fill (purple for one subject, pink for another), a `6 / 8` count label at the end, and a small trophy/badge icon.
- Footer meta line: "Next up: …" in `caption`, `--color-text-muted`.

### 5.4 Activity / Lesson Card (small)
- Compact white card, `--radius-lg`, `--shadow-xs`, padding `--space-4`.
- Top row: subject name (`h3`, smaller) + a **status pill** (Completed / In-Progress / Not Started).
- Middle: a numbered chip ("02") + lesson name + a small illustration icon.
- "Time: X minutes" meta in `caption` with a clock icon.
- Thin progress bar with `4 / 4` fraction.
- Full-width text button "View Lesson" in `--color-primary`.
- Lay these out in a horizontal scroll row or responsive grid (4 across on desktop).

### 5.5 Status Pills / Badges
- `--radius-pill`, padding `2px 10px`, `caption` weight 600, a 6px leading dot.
| State | Text color | Background | Dot |
|---|---|---|---|
| Completed | `--color-success` | `--color-success-soft` | green |
| In-Progress | `--color-warning` | `--color-warning-soft` | amber |
| Not Started | `--color-neutral` | `--color-neutral-soft` | grey |
| Role/Grade | `--color-primary` | `--color-primary-soft` | none |

### 5.6 Progress Bar
- Track: height 8px, `--radius-pill`, `--color-neutral-soft`.
- Fill: same height/radius, subject color, animated width transition (`200ms ease`).
- Optional fraction label (`4 / 4`) trailing the bar in `caption`.

### 5.7 Buttons
| Variant | Style |
|---|---|
| Primary | Solid `--color-primary`, white text, `--radius-md`, padding `10px 18px`, `label` type, `--shadow-xs`; hover → `--color-primary-hover`. |
| Secondary / Outline | White bg, `--color-primary` text, 1px `--color-primary` border, `--radius-md` (e.g. "Next Grade"). |
| Ghost / Text | No bg, `--color-primary` text (e.g. "View Lesson"). |
| Marketing CTA | Solid `--color-accent-yellow`, `--color-text` (near-black) text, `--radius-pill`, padding `14px 28px`, weight 700, arrow icon (e.g. "Explore All Courses"). |
| Toggle group | Segmented control (Kanban / List, Week selector): pill container `--color-neutral-soft`, active segment solid white or `--color-primary`. |

### 5.8 Forms & Inputs
- Inputs: white bg, 1px `--color-border`, `--radius-md`, padding `10px 14px`, `body` type.
- Focus: border `--color-primary`, 3px `--color-primary-ring` glow.
- Labels above inputs in `label` type, `--color-text-secondary`.
- File upload (course materials): dashed `--color-border-strong` drop zone, `--radius-lg`, upload icon + "Add File" — matches the assignment's upload UI.

### 5.9 Tabs / Segmented Views
- Used for "Kanban / List" and "Weekly Activity". Pill-style segmented control; the Kanban board uses day columns as light panels (`--color-surface-alt`, `--radius-lg`) each holding activity cards.

### 5.10 Avatars & Chat (WebSocket module)
- Avatars: circular, `--radius-pill`, with a thin white ring; stacked/overlapping for groups ("Trusted by 4k+ students" cluster on landing).
- Chat: message bubbles `--radius-lg` (tail-less), own messages `--color-primary` bg / white text right-aligned, others `--color-surface-alt` / `--color-text` left-aligned. Composer is a rounded input + primary send button.

---

## 6. Marketing / Landing Theme (public + auth pages)

Applies to the landing page, login and registration.

- **Background:** large soft sky-blue (`--color-sky`) organic blobs / rounded panels behind a white rounded content sheet (`--radius-2xl`).
- **Hero:** centered, oversized black `display` headline with the brand mark inline; short `body` subtitle in `--color-text-secondary`; a single yellow pill CTA.
- **Trust strip:** overlapping circular avatars + "Trusted by 4k+ students" in `label`.
- **Feature blocks:** chunky rounded cards (`--radius-2xl`) in green (`--color-accent-green`) and yellow (`--color-accent-yellow`) with black text; one photo card with a small white caption card overlapping its corner.
- **Illustrations:** friendly line/spot illustrations (graduation cap, rocket, chat bubbles) scattered as decoration. Optional hand-written script accents (`Caveat`) for playful section labels.
- **Nav:** transparent over the white sheet — left wordmark, centered links (Home/About/Courses/Contact), right search icon + black pill "Sign Up" button.

Keep the marketing theme **only** on public pages; once logged in, the user drops into the calm App Theme.

---

## 7. Iconography & Illustration
- **Icons:** Lucide (line, 20px, 1.75 stroke) throughout the app for consistency.
- **Illustrations:** soft, colorful spot illustrations for KPI cards and empty states. Use an open set (e.g. Storyset / unDraw) tinted toward the palette. Never mix illustration styles.
- **Empty states:** centered illustration + one-line explanation + a primary action.

---

## 8. Motion
- Card hover: lift shadow `--shadow-sm` → `--shadow-md`, `150ms ease`.
- Progress fills animate width on load, `400ms ease-out`.
- Nav active-state and buttons: `120ms ease` color transitions.
- Modals/drawers: fade + 8px rise, `180ms`. Keep motion subtle and fast — nothing bounces.

---

## 9. Responsive Behavior
- **≥1200px:** full sidebar + multi-column card grids (KPI x3, activity x4).
- **768–1199px:** sidebar remains; grids collapse to 2 columns.
- **<768px:** sidebar collapses to an icon rail or off-canvas drawer (hamburger in a top bar); cards stack single-column; horizontal card rows become swipeable.

---

## 10. Accessibility
- Body text contrast ≥ 4.5:1; large text ≥ 3:1. (Yellow marketing buttons use near-black text to pass.)
- Visible focus ring (`--color-primary-ring`) on every interactive element.
- Status is never conveyed by color alone — always paired with a text label.
- All icons that carry meaning get `aria-label`; decorative illustrations get `aria-hidden`.
- Respect `prefers-reduced-motion` — disable non-essential transitions.

---

## 11. Implementation Notes (for Claude Code)
- Put all tokens in a single `static/css/tokens.css` imported first; build components against variables only.
- If using Bootstrap, override its Sass variables to these tokens (map `$primary`, `$border-radius`, `$font-family-base`, etc.) rather than fighting defaults — this counts as "advanced technique" in the rubric.
- Base template (`base.html`) implements the App Shell (sidebar + header + content slot); a separate `base_public.html` implements the Marketing Theme for landing/auth.
- Build a small component partial set: `_sidebar.html`, `_kpi_card.html`, `_course_card.html`, `_activity_card.html`, `_status_pill.html`, `_progress_bar.html`, `_button` macros — so views stay clean and styling is consistent.
- Keep the color/subject mapping (math=purple, reading=pink) as a template helper, not hardcoded per template.
