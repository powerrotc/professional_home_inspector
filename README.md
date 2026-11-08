# Professional Home Inspection

A bilingual-ready web platform for a professional home inspection business serving British Columbia, Canada.

## Project goals

Build a reliable, mobile-friendly website and operations system with:
- Public business information and inspection service pages.
- Customer enquiries and AI-assisted customer Q&A.
- Inspection booking requests and availability collection.
- Administrator review and approval of appointments, including proposing up to three time options.
- Five-hour default inspection appointment duration (configurable by an administrator).
- Quote preparation based on property characteristics and transparent pricing rules.
- Email notifications and Google Calendar integration.
- Secure administrator authentication and an enquiry/booking management dashboard.
- Audit-friendly workflows and clear customer communications.

## Technology direction

The initial target architecture is:
- Frontend: React / Next.js.
- Backend: Python / FastAPI.
- Relational database: Neon PostgreSQL free tier.
- Hosting: Render free tier, subject to its current resource and sleep limits.
- Source control and review: GitHub Free.
- AI: a provider/API only if it has a usable free tier; enforce usage limits and never enable paid billing without explicit owner approval.
- Email and calendar: free Google account integrations where permitted by the relevant quotas and terms.

Service availability, free-tier quotas, and provider terms can change. Verify current limits before depending on a service. Do not add paid services, paid plans, paid add-ons, or billing commitments.

## Development rules

See [AGENTS.md](AGENTS.md) for mandatory instructions for human developers and AI coding agents.

## Data and privacy

- The previous prototype's test data, local Gemma model, RAG database, PDFs, and embeddings are intentionally out of scope. Do not import them.
- Use synthetic test data only during development.
- Never commit credentials, API keys, OAuth tokens, private customer information, or production data.
- Keep secrets in deployment environment variables.
- Design for data minimization, access control, and secure handling of customer contact and property information.

## Current status

The first application foundation is implemented on `main`: a public website, guided FAQ, enquiry API (disabled until persistent storage is configured), admin API/dashboard, tests, and Render Free Blueprint. The first Render demo deployment is still pending; no live server URL exists yet. See [deployment instructions](docs/DEPLOYMENT.md).

## Owner approvals

- Work on feature branches and submit pull requests for review.
- Do not merge pull requests, deploy, change production configuration, enable paid billing, or perform irreversible data operations without explicit owner approval.
