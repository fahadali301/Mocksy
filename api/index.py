import json
import logging
import threading
from typing import Any

try:
    from mangum import Mangum
except Exception:  # pragma: no cover - runtime dependency safety
    Mangum = None

_handler = None
_handler_lock = threading.Lock()
_startup_error = None

logger = logging.getLogger(__name__)


def _initialize_handler():
    global _handler, _startup_error
    if _handler is not None or _startup_error is not None:
        return

    with _handler_lock:
        if _handler is not None or _startup_error is not None:
            return

        try:
            if Mangum is None:
                raise RuntimeError("Mangum is not installed. Add 'mangum' to requirements.")

            from app.core.config import validate_environment
            from app.core.database import check_database_connection
            from app.index import app

            startup_issues = validate_environment()
            app.state.startup_issues = startup_issues

            try:
                check_database_connection(retries=3, delay=0.75)
                app.state.database_available = True
            except Exception as db_exc:
                app.state.database_available = False
                app.state.startup_issues = startup_issues + [
                    f"Database connection failed: {str(db_exc)}"
                ]
                logger.warning("Database unavailable during cold start: %s", db_exc)

            _handler = Mangum(app, lifespan="off")
        except Exception as exc:
            _startup_error = str(exc)
            logger.exception("Failed to initialize serverless handler")


def handler(event: dict[str, Any], context: Any):
    _initialize_handler()

    if _handler is None:
        return {
            "statusCode": 500,
            "headers": {"content-type": "application/json"},
            "body": json.dumps(
                {
                    "status": "error",
                    "message": "Serverless initialization failed.",
                    "detail": _startup_error or "Unknown startup error.",
                }
            ),
        }

    return _handler(event, context)
