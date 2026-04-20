# Vercel FastAPI Crash Fix Guide (Mocksy)

## 1. Configure Vercel Environment Variables
In **Vercel → Project → Settings → Environment Variables**, add:

- `DATABASE_URL` (PostgreSQL, SQLAlchemy format)
- `SECRET_KEY` (long random string)
- `ALGORITHM` (`HS256`)
- `DEBUG` (`False`)
- `CORS_ORIGINS` (frontend domain)
- `GROQ_ENABLED` (`True`/`False`)
- `GROQ_API_KEY` (required if `GROQ_ENABLED=True`)

Use `.env.production` as the template.

## 2. Verify Database Connectivity
Use your DB provider query tool and run:

```sql
SELECT 1;
```

Confirm the same host/user/password/dbname are used in `DATABASE_URL`.

## 3. Run Migrations (Important)
Do **not** rely on runtime table creation.

```bash
alembic upgrade head
```

## 4. Deploy Verification
After redeploy, verify:

- `GET https://<project>.vercel.app/api/`
- `GET https://<project>.vercel.app/api/docs`

If DB is unavailable, `/api/` may return a degraded status with startup issues for debugging.

## 5. Troubleshooting
- `FUNCTION_INVOCATION_FAILED`: usually missing/invalid `DATABASE_URL` or `SECRET_KEY`.
- `500 INTERNAL_SERVER_ERROR` on cold start: verify env vars and DB network access.
- Auth errors: verify `SECRET_KEY` and token settings.
- AI features failing: set valid `GROQ_API_KEY` or disable via `GROQ_ENABLED=False`.
