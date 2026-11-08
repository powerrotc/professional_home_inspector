# AGENTS.md — Development and AI Agent Instructions

These instructions apply to ChatGPT, the owner's Personal AI Agent, and all human contributors working in this repository.

## 1. Project mission

Develop and maintain the Professional Home Inspection web application for a home inspection business in British Columbia, Canada. The product must support customers and administrators, be secure, mobile-friendly, maintainable, and suitable for future incremental development by another AI agent.

## 2. Non-negotiable cost constraint

- Use free plans and free-tier services only.
- Never enable billing, subscribe, purchase credits, select paid add-ons, or intentionally exceed a free quota.
- Before adopting a provider, verify its current free-tier terms, limits, and suitability. Free tiers can change.
- If a required capability cannot be delivered within the free constraint, explain the limitation and present free alternatives. Do not silently introduce a paid dependency.
- Include sensible rate limits, usage caps, and graceful handling of quota exhaustion for AI and external APIs.

## 3. Architecture direction

Preferred starting point:
- Frontend: React / Next.js.
- Backend: Python / FastAPI.
- Database: Neon PostgreSQL free tier.
- Hosting: Render free tier.
- Repository and CI: GitHub Free / GitHub Actions within available free usage.
- AI: a model/API with an available free allowance, behind a provider-neutral interface where practical.
- Integrations: Google Calendar and Gmail using supported free account/API quotas.

Do not assume any free tier is unlimited or permanently available. Re-check current provider limits before implementation and document operational trade-offs (for example, cold starts, sleeping services, storage persistence, request limits, and monthly quotas).

## 4. Product requirements

Preserve these requirements unless the owner explicitly changes them:
- Public-facing business website for British Columbia customers.
- Responsive design for desktop and mobile.
- Customer enquiry and AI-assisted Q&A.
- Inspection booking request flow that collects customer availability.
- Administrator approval before a booking becomes confirmed.
- Offer up to three proposed appointment times when coordinating availability.
- Default inspection duration: five hours, configurable.
- Quote preparation based on house size and relevant property characteristics; pricing must be transparent and subject to administrator review before sending.
- Google Calendar integration for approved appointments.
- Gmail/email integration for customer and administrator notifications, subject to free quotas.
- Secure admin login and an admin dashboard for enquiries and bookings.
- Deleted enquiries view with pagination (10 items per page), subject to a clear retention policy.
- Time zone: America/Vancouver.
- British Columbia property lookup/BC Assessment integration is postponed. Do not scrape BC Assessment or depend on unofficial datasets. Revisit only when the owner requests it and an authorized data access method is confirmed.

## 5. Fresh start and data handling

- Do not reuse or migrate the former prototype's test data, Gemma model files, Ollama configuration, RAG database, uploaded PDFs, or embedding vectors.
- Generate synthetic fixtures for development and automated tests.
- Never use real customer data in tests, examples, screenshots, logs, or commits.
- Do not commit secrets or local environment files. Provide a safe environment example file with placeholder values only.
- Validate and minimize customer data collection. Protect personal and property information with appropriate authorization and access controls.
- Do not claim compliance with a legal or security standard unless it has been assessed.

## 6. Collaboration and handoff

The repository is the shared source of truth for both ChatGPT and the owner's Personal AI Agent.
- Read this file and the README before making changes.
- Keep architecture decisions, setup instructions, environment variables, deployment steps, and operational procedures documented in the repository.
- Maintain a concise project status / handoff document (for example, docs/PROJECT_STATUS.md) with completed work, current state, known issues, next tasks, and verification results.
- For substantial features, add or update tests and documentation in the same change.
- Prefer small, isolated changes that are easy for another agent to understand and review.
- Do not rely on undocumented conversation history; record durable decisions in repository documentation.
- Never expose credentials in logs, source code, pull request descriptions, or documentation.

## 7. Git and approval workflow

- Never commit feature work directly to main.
- Create a descriptive branch for each task (for example, feature/customer-booking or fix/booking-validation).
- Open a pull request targeting main, summarizing changes, tests, risks, and any configuration required.
- Run relevant tests and inspect the diff before requesting review.
- Do not merge a pull request unless the owner explicitly approves that specific merge.
- Do not deploy, modify production environment variables, change DNS, enable external integrations in production, or run destructive migrations without explicit owner approval.
- Do not create paid resources or enable paid billing under any circumstances without explicit owner approval; the project constraint remains free-only unless the owner changes it.
- Ask the owner before any irreversible operation or any action that sends real customer communications.

## 8. Engineering quality

- Use typed interfaces and clear separation between frontend, API, persistence, and external integrations.
- Validate all incoming data server-side.
- Enforce authentication and authorization on administrative endpoints.
- Store passwords using a suitable password-hashing algorithm; never store plaintext passwords.
- Keep CORS origins restrictive in deployed environments.
- Use parameterized database queries / ORM protections.
- Add automated tests for core business rules, booking approval, quote calculations, access control, and integration failure paths.
- Handle external API errors, timeouts, retries, and quota exhaustion safely.
- Avoid logging personal information, tokens, or sensitive request bodies.
- Include health checks and deployment configuration appropriate to the chosen free hosting tier.

## 9. Definition of done

A feature is not complete merely because code was written. Before marking it complete:
1. Tests pass (or any unavailable test is explicitly documented).
2. The diff has been reviewed for security, privacy, and accidental secrets.
3. Documentation and handoff status are updated.
4. Free-tier compatibility has been checked.
5. Deployment is verified only if an authorized deployment was actually performed.
6. The pull request clearly states what remains incomplete.

## 10. Communication

Report progress in clear, concise Korean to the owner unless the owner requests another language. Explain blockers and limitations honestly. Ask one focused question at a time when owner input is required.
