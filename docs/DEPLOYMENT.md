# First Render demo deployment

The repository now contains a Render Blueprint at `render.yaml`. It creates one Python web service on the **Free** plan and starts in demo mode without requiring secrets.

## Create the first demo service

1. Sign in to the Render dashboard: https://dashboard.render.com/.
2. Choose **New + → Blueprint**.
3. Connect the GitHub repository `powerrotc/professional_home_inspector` and select the `main` branch.
4. Review the Blueprint and verify the service plan says **Free**. Do not add a paid disk, paid database, paid add-on, or billing commitment.
5. Apply the Blueprint and wait for the first deploy to finish.
6. Open the generated `.onrender.com` service URL. Check `/api/health` and confirm `status=ok`, `database_mode=sqlite-demo-only`, and `submissions_enabled=false`.

The homepage and guided FAQ can be previewed in this demo. The enquiry form intentionally refuses submissions. Do not enter real customer information in demo mode.

## Database schema migrations

The project now includes Alembic with a non-destructive baseline migration.

- For a new database, run `alembic upgrade head` with `DATABASE_URL` pointing to that database before deploying code that depends on schema changes.
- For a database created by the earlier application's `Base.metadata.create_all()`, the baseline checks that the expected tables and columns already exist and adds the enquiry lookup index only if it is missing. It does not drop tables, rewrite rows, or change customer data.
- If an existing table is missing an expected column, the migration stops with an error instead of guessing how to repair data.
- The baseline migration is intentionally non-reversible. Do not run `alembic downgrade` against it.
- The current demo startup still calls SQLAlchemy `create_all()` for compatibility. Treat Alembic—not `create_all()`—as the versioned schema-change record for future development.
- Never run migrations against the production Neon database until the owner explicitly approves that production operation. Test migrations against a disposable SQLite database first.

Example local command (use a disposable database):
```bash
DATABASE_URL=sqlite:///./migration-test.db alembic upgrade head
```

## Before accepting real enquiries

1. Create a separate Neon project on its Free plan; do not reuse the Personal AI Agent database.
2. Copy the PostgreSQL connection string and set `DATABASE_URL` in the Render service's Environment settings.
3. Generate a password hash locally with `python -m app.security hash-password` (use a unique password of at least 12 characters). Put the resulting `scrypt$...` string in Render as `ADMIN_PASSWORD_HASH`. Do not put the raw password in Render or source control.
4. Generate a separate random session secret (at least 32 characters) and set it as `ADMIN_SESSION_SECRET` in Render. Keep both values private.
5. Redeploy, then verify `/api/health` reports `database_mode=postgresql`, `persistent_storage_configured=true`, and `admin_configured=true`.
6. Open `/admin`, sign in, verify the session cookie is Secure, HttpOnly, and SameSite=Strict, and test sign-out.
7. Only after all security and data-retention checks pass, consider setting `ALLOW_PUBLIC_SUBMISSIONS=true`. Keep it false until the owner explicitly approves accepting real enquiries.

## Free-tier limitations

Render Free web services are intended for preview/hobby use, not production. They spin down after 15 minutes without inbound traffic, the next request can take about a minute to wake, and the local filesystem is ephemeral. Never rely on local SQLite for customer records.

Neon Free has finite compute, storage, and network allowances. Review its current dashboard usage and limits. If a quota is reached, do not upgrade or enable billing; pause and find a free alternative.

## Current status

- Application code and CI are maintained in GitHub; a merged PR does not prove that a Render deployment is live.
- Render Blueprint is ready.
- The Render account connection is not available to the current ChatGPT tools; a one-time owner sign-in and Blueprint application is required to create or verify the service.
