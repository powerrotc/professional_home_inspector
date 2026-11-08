# Free demo deployment

## Render Blueprint

1. In Render, choose **New + → Blueprint** and connect `powerrotc/professional_home_inspector`.
2. Select the `feature/application-foundation` branch for the first preview if Render offers branch selection; otherwise merge the reviewed PR to `main` first.
3. Confirm the service plan is **Free**. Do not add a paid disk, paid database, or paid add-on.
4. The Blueprint creates one Python web service. Configure secrets only in the Render dashboard, never in GitHub.
5. The app can be viewed in demo mode without credentials, but public submissions remain disabled.

## Persistent database before accepting enquiries

Create a separate Neon project on its free plan. Copy its pooled or direct PostgreSQL connection string and set it as `DATABASE_URL` in Render. Confirm `/api/health` reports `database_mode=postgresql` and `persistent_storage_configured=true`.

Set a long random `ADMIN_API_KEY` in Render. Open `/admin` and verify the key grants access. Only after both checks succeed, set `ALLOW_PUBLIC_SUBMISSIONS=true`.

## Health check

Open `/api/health`. The initial demo should return status `ok`. If the database mode is `sqlite-demo-only`, do not submit real customer information; Render's local filesystem is not durable.

## Free-tier caveats

Free web services can sleep when idle and may have cold starts, limited CPU/RAM, and no durable local filesystem. Neon free quotas and policies can change. Confirm current limits in the provider dashboards. Never enable billing to resolve a quota issue; pause and choose a free alternative instead.
