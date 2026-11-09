# Project Status and Agent Handoff

Last updated: 2026-11-09

## Current baseline
- Repository: `powerrotc/professional_home_inspector`
- Hosting target: Render Free; database target: separate Neon Free project named Home Inspector.
- Default timezone: `America/Vancouver`.
- Synthetic test data only. Do not import legacy prototype data.
- PR #4 (secure administrator login), #5 (admin enquiry and booking workflows), #6 (homepage hero image/design), and #7 (Alembic baseline migration) are merged to `main`.
- PR #7 establishes a non-destructive baseline; do not run production migrations until separately approved.
- Production Render environment variables have not been changed through this development workflow.
- Public submissions must remain disabled until persistent PostgreSQL, secure admin login, and owner-approved readiness checks are complete.

## Implemented
- Responsive public website with a high-impact home-inspector hero image and clear enquiry calls to action.
- Guided FAQ (not generative AI).
- Enquiry API with validation; public submissions disabled by default.
- Admin password verification using salted scrypt hashes.
- Signed eight-hour admin sessions in Secure, HttpOnly, SameSite=Strict cookies.
- Same-origin checks on state-changing admin routes.
- Admin enquiry listing with active/deleted/all filters and 10-item pagination.
- Up to three appointment proposal records; saving a proposal does not send customer communication.
- Render Free Blueprint and deployment guide.
- Alembic migration history with a non-destructive baseline for existing and fresh databases.
- Administrator-configurable quote rules (CAD base fee, per-square-foot rate, minimum fee).
- Quote drafts use max(minimum fee, base fee + property size × rate), are stored for review, and are never sent automatically.

## Quote calculation limitations
- No business prices are prefilled or invented; the administrator must enter approved amounts.
- The quote is a preliminary subtotal only. Taxes, travel, special property conditions, and additional adjustments are excluded and require manual review.
- Property type is recorded for context but does not alter the formula until the owner supplies approved adjustment rules.
- The formula is not customer-facing and does not represent a final offer.

## Known limitations
- Admin dashboard requires `ADMIN_PASSWORD_HASH` and `ADMIN_SESSION_SECRET` on Render.
- `DATABASE_URL` must point to the separate Home Inspector Neon project; SQLite is demo-only and Render local storage is ephemeral.
- Admin login rate limiting is process-local and may reset when a free service sleeps/restarts or when multiple workers are used; add platform-level protection before production.
- Enquiry status can restore an item from the deleted view. Permanent deletion and a retention policy are not implemented.
- Appointment proposals are stored as draft records only; there is no customer email, customer acceptance flow, or Calendar sync.
- Generative AI, Gmail, Google Calendar, and BC Assessment lookup are not implemented.
- Do not use real customer records or send external messages in testing.

## Next tasks
1. Add tests for quote rules, quote calculation, and migration upgrade paths; confirm CI.
2. Review deployment sync and health checks only with owner-approved production operations.
3. Evaluate provider-neutral AI Q&A only after confirming a usable free allowance and implementing hard usage caps.
4. Evaluate Gmail and Google Calendar only after free-quota review and explicit production authorization.
5. Define retention policy before permanent deletion is implemented.

## Deployment safety
- Render service: `https://professional-home-inspection.onrender.com/`
- Keep `ALLOW_PUBLIC_SUBMISSIONS=false`.
- Never expose passwords, hashes, session secrets, database URLs, OAuth credentials, or customer details.
- No paid services, plans, add-ons, credits, or billing.
