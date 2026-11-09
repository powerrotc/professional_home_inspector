# Project Status and Agent Handoff

Last updated: 2026-11-08

## Current baseline
- Repository: `powerrotc/professional_home_inspector`
- Hosting target: Render Free; database target: separate Neon Free project named Home Inspector.
- Default timezone: `America/Vancouver`.
- Synthetic test data only. Do not import legacy prototype data.
- PR #4 (secure administrator login) merged to `main` as `55ccaba7a0adc59e9cc58f0215fbed9be3db4ba5`.
- Production Render environment variables were not changed.
- Public submissions must remain disabled until persistent PostgreSQL, secure admin login, and owner-approved readiness checks are complete.

## Implemented
- Responsive public website and guided FAQ (not generative AI).
- Enquiry API with validation; public submissions disabled by default.
- Admin password verification using salted scrypt hashes.
- Signed eight-hour admin sessions in Secure, HttpOnly, SameSite=Strict cookies.
- Same-origin checks on state-changing admin routes.
- Admin enquiry listing with active/deleted/all filters and 10-item pagination.
- Up to three appointment proposal records; saving a proposal does not send customer communication.
- Render Free Blueprint and deployment guide.

## In progress
- PR #4 merge completed. A post-merge workflow run was not returned by the current GitHub workflow lookup; do not report post-merge CI as verified.
- PR #5 (admin enquiry workflow UI) adds status management, restore-by-status-change, appointment proposal entry, and proposal listing. CI and review pending.

## Known limitations
- Admin dashboard requires `ADMIN_PASSWORD_HASH` and `ADMIN_SESSION_SECRET` on Render.
- `DATABASE_URL` must point to the separate Home Inspector Neon project; SQLite is demo-only and Render local storage is ephemeral.
- Admin login rate limiting is process-local and may reset when a free service sleeps/restarts or when multiple workers are used; add platform-level protection before production.
- Enquiry status can restore an item from the deleted view. Permanent deletion and a retention policy are not implemented.
- Appointment proposals are stored as draft records only; there is no customer email, customer acceptance flow, or Calendar sync.
- Quote calculation, generative AI, Gmail, Google Calendar, and BC Assessment lookup are not implemented.
- Do not use real customer records or send external messages in testing.

## Next tasks
1. Verify PR #5 CI and inspect its complete diff.
2. Add safe, versioned database migrations before future schema changes; do not run destructive migrations.
3. Add configurable quote rules as draft calculations subject to administrator review; do not invent business prices.
4. Add provider-neutral AI Q&A only after confirming a usable free allowance and implementing hard usage caps.
5. Evaluate Gmail and Google Calendar only after free-quota review and explicit production authorization.
6. Complete Render configuration and health checks only with owner-approved production changes.

## Deployment safety
- Render service: `https://professional-home-inspection.onrender.com/`
- Keep `ALLOW_PUBLIC_SUBMISSIONS=false`.
- Never expose passwords, hashes, session secrets, database URLs, OAuth credentials, or customer details.
- No paid services, plans, add-ons, credits, or billing.
