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

## Before accepting real enquiries

1. Create a separate Neon project on its Free plan; do not reuse the Personal AI Agent database.
2. Copy the PostgreSQL connection string and set `DATABASE_URL` in the Render service's Environment settings.
3. Set a long random `ADMIN_API_KEY` in Render.
4. Redeploy, then verify `/api/health` reports `database_mode=postgresql`, `persistent_storage_configured=true`, and `admin_configured=true`.
5. Open `/admin` and verify admin authentication works.
6. Only then set `ALLOW_PUBLIC_SUBMISSIONS=true` and redeploy.

## Free-tier limitations

Render Free web services are intended for preview/hobby use, not production. They spin down after 15 minutes without inbound traffic, the next request can take about a minute to wake, and the local filesystem is ephemeral. Never rely on local SQLite for customer records.

Neon Free currently has finite compute, storage, and network allowances. Review its current dashboard usage and limits. If a quota is reached, do not upgrade or enable billing; pause and find a free alternative.

## Current status

- Code and CI are merged to `main`.
- Render Blueprint is ready.
- No Render service has been created from this chat session, so there is no live URL to share yet.
- The Render account connection is not available to the current ChatGPT tools; a one-time owner sign-in and Blueprint application is required to create the service. Once the service exists, its URL can be used for verification.
