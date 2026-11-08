# Project status and handoff

Last updated: 2026-11-08

## Current milestone

First application foundation is being prepared for a demo deployment. Work is on `feature/application-foundation`; `main` remains protected by the owner review workflow.

## Implemented in this milestone

- FastAPI web application serving a responsive public website.
- Service overview and customer enquiry form UI.
- Guided FAQ assistant for common questions (not yet a generative AI model).
- Enquiry API with server-side validation.
- Admin API protected by an environment API key.
- Admin enquiry list with 10 records per page and active/deleted/all filters.
- Up to three proposed appointment time fields per enquiry.
- Health endpoint reporting whether persistent PostgreSQL storage and admin configuration are present.
- Render Blueprint for a free Python web service.
- Automated smoke tests and GitHub Actions CI.

## Deliberately not enabled yet

- Public enquiry submissions remain disabled unless a persistent PostgreSQL database is configured and `ALLOW_PUBLIC_SUBMISSIONS=true`.
- SQLite fallback is for local/demo smoke tests only; Render disk storage is ephemeral on the free web service.
- No real customer data should be entered during the demo deployment.
- No live Gemini/LLM provider, Gmail, or Google Calendar credentials have been configured for this separate application.
- No business contact details, final pricing table, insurance/licensing claims, or service-area boundaries have been supplied; do not invent them.
- BC Assessment lookup remains postponed.

## Deployment requirements

1. Create a separate free Neon PostgreSQL database for this project; do not reuse the Personal AI Agent database.
2. Set `DATABASE_URL` to the Neon connection string in Render.
3. Set a long random `ADMIN_API_KEY` in Render.
4. Set `ALLOW_PUBLIC_SUBMISSIONS=true` only after the database connection and admin access have been verified.
5. Keep all Render services on the Free plan. Do not add a paid persistent disk or paid service.

## Known limitations / next tasks

- Verify Render free-tier service and sleep behavior at deployment time.
- Connect the repository to Render using the included `render.yaml` Blueprint.
- Verify deployment health and public page rendering.
- Configure Neon PostgreSQL and verify persistence across service restarts.
- Add secure admin login/session handling (current admin API key is a temporary owner-only bootstrap mechanism).
- Add proposal review and customer acceptance flow, calendar sync, email notifications, and an audited quote workflow.
- Add a provider-neutral AI adapter and a free-tier provider only after verifying current terms and adding strict usage caps.
- Add retention-aware deleted-enquiry pagination and restore/permanent-delete policy before enabling destructive deletion.

## Verification

Automated tests are defined in `tests/test_app.py` and run via GitHub Actions. A successful CI run is required before merge. A successful GitHub merge alone does not prove a Render deployment is live.
