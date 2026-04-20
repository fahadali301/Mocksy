# Vercel Production Deployment (Mocksy Backend)

## 1) Prerequisites
- GitHub repo connected to Vercel (`fahadali301/Mocksy`)
- PostgreSQL database ready (recommended: Supabase or Neon)
- Groq API key

## 2) Vercel project setup
1. Go to [vercel.com](https://vercel.com) → **Add New Project**
2. Import `fahadali301/Mocksy`
3. Keep root directory as repository root
4. Deploy

## 3) Configure environment variables
In Vercel Project → **Settings** → **Environment Variables**, add:

- `DATABASE_URL` = PostgreSQL connection string
- `SECRET_KEY` = long random secret
- `GROQ_API_KEY` = your Groq API key
- `ALGORITHM` = `HS256`
- `DEBUG` = `False`
- `GROQ_ENABLED` = `True` (optional, but recommended for current AI flow)

Use `.env.example` as the source of truth for variable names.

## 4) Routing and serverless handler
- `api/index.py` is the Vercel serverless entry point.
- `vercel.json` rewrites `/api/*` to the Python serverless function.
- API base URL after deployment:
  - `https://<your-project>.vercel.app/api/`

## 5) Validate deployment
After deploy, test:
- `GET https://<your-project>.vercel.app/api/`
- `GET https://<your-project>.vercel.app/api/docs`

Expected health response:
```json
{"status":"ok","message":"Mocksy API is running"}
```

## 6) Troubleshooting
- **500 on startup**: verify `DATABASE_URL` and database network access.
- **401/Token issues**: confirm `SECRET_KEY` and `ALGORITHM` values.
- **AI not responding**: check `GROQ_API_KEY` and `GROQ_ENABLED`.
- **Route not found**: make sure requests go through `/api/...`.
