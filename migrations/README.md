# Migrations

Mocksy uses **Alembic** for schema management.

## Why this directory exists
Runtime table creation has been removed from app startup. Database schema must be managed via migrations.

## Commands

Create a migration:

```bash
alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback one migration:

```bash
alembic downgrade -1
```

Migration scripts are stored in `alembic/versions/`.
