# Day 8 — Changes Summary

Status: built and verified working locally. **Not yet pushed** — still sitting
as staged/unstaged changes on `main` per `git status`.

---

## 1. JWT Authentication (built from scratch)

The project had no working auth layer before this — the dashboard already
called `POST /api/auth/login` and expected a JWT back, but nothing on the
backend implemented it.

**New files:**
- `entity/User.java` — `app_user` table (username, BCrypt password hash, role)
- `repository/UserRepository.java` — `findByUsername`
- `security/JwtService.java` — generates/validates HS256 tokens
- `security/CustomUserDetailsService.java` — loads `User` for Spring Security
- `security/JwtAuthenticationFilter.java` — per-request Bearer token validation
- `security/SecurityConfig.java` — filter chain, CORS, password encoder, auth manager
- `security/DataSeeder.java` — dev-only seed user on startup (`demo_user` / `ChangeMe123!`)

**Modified:**
- `controller/AuthController.java` — `POST /api/auth/login`, returns `{"token": "..."}` on success, `401 {"error": "..."}` on bad credentials

**Cleanup during the same work:**
- Removed `config/SecurityConfig.java` (duplicate — CORS/security now lives in one place, `security/SecurityConfig.java`, to avoid two competing `SecurityFilterChain` beans)
- Removed `security/JwtAuthFilter.java` (old name, superseded by `JwtAuthenticationFilter.java`)
- Removed `security/JwtServiceOg.java` (backup of the pre-JWT `JwtService.java`, no longer needed)

## 2. Ticket Service bug fixes

`service/TicketService.java`:
- Added the missing `listAllTickets()` method — `TicketController`'s `GET /api/tickets` was calling this method, but it didn't exist, so the project wouldn't compile
- `createTicket()` now explicitly sets `status("OPEN")` instead of relying only on the entity's default (the `Ticket` entity's own `@PrePersist` fallback is still there too — harmless belt-and-braces)

## 3. Dashboard redesign

`static/index.html` — rebuilt from a basic Bootstrap page into a dark,
purpose-built dashboard:
- 4 stat cards (Total tickets, Open, High+Critical priority, Services tracked) — all computed from real ticket data, nothing fabricated
- 2 charts (Chart.js) — tickets by status, tickets by priority — built dynamically from whatever status/priority values actually appear in the data
- Search box to filter the ticket list
- "New ticket" modal with client-side validation: title ≥ 8 chars, description ≥ 30 chars (live counter), service name (datalist suggests existing names to avoid typo-duplicated services), priority (explicit dropdown, no silent default)
- Removed hardcoded demo credentials (`mentor_demo` / `changeme_demo_password`) from the login form

**Bug found and fixed after first deploy:** Chart.js was loaded from a
cdnjs URL that failed to resolve, causing a `ReferenceError: Chart is not
defined`. This exception was also bubbling up and wiping out the
already-rendered ticket list (a bug in the original error handling, not
just the CDN link). Fixed by:
- Switching the Chart.js `<script>` tag to jsDelivr (`cdn.jsdelivr.net/npm/chart.js@4.4.1`) — same provider already working for Bootstrap
- Isolating chart-rendering failures so they only affect the chart cards, never the ticket list or stats

## 4. Ticket quality guidance

Documented why bad tickets hurt prediction quality (`TicketController.ticketText()`
concatenates title + description verbatim and sends it straight to the
model — no cleanup step), and what "good" looks like: specific titles,
detailed descriptions, reused service names, honestly-chosen priority.
The dashboard's new-ticket form enforces the client-side version of this;
server-side validation (`@Valid` + Bean Validation annotations on
`TicketCreateRequest`) was discussed as a follow-up, not yet implemented.

---

## Files touched (matches `git status`)

**New:** `entity/User.java`, `repository/UserRepository.java`,
`security/CustomUserDetailsService.java`, `security/DataSeeder.java`,
`security/JwtAuthenticationFilter.java`, `security/SecurityConfig.java`,
`static/index.html`

**Modified:** `controller/AuthController.java`, `controller/TicketController.java`,
`security/JwtService.java`, `service/TicketService.java`

**Deleted:** `config/SecurityConfig.java`, `security/JwtAuthFilter.java`,
`security/JwtServiceOg.java`

## Before you push — two things worth a second look

- `docker-compose.yml` shows as modified but wasn't touched as part of this
  session's work — worth checking `git diff docker-compose.yml` before
  committing, in case it's an unrelated change or a stray auto-edit.
- `digest.txt` is showing as untracked — that's the working file used to
  share context during this session, not project source. Probably belongs
  in `.gitignore` rather than committed.

---

*This file documents the actual code changes made and verified in this
session. It's intentionally kept separate from `memory.md` rather than
appended to its existing changelog — merge it in yourself if and where it
fits your project's real history.*
