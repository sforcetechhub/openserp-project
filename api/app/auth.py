from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app.config import settings

PUBLIC_PATHS = {"/", "/health", "/favicon.ico", "/docs", "/redoc", "/openapi.json"}
PUBLIC_PREFIXES = ("/static",)


def is_public_path(path: str) -> bool:
    if path in PUBLIC_PATHS:
        return True
    return any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES)


def credentials_match(authorization: str | None) -> bool:
    if not settings.auth_required:
        return True
    if not authorization:
        return False
    scheme, _, token = authorization.partition(" ")
    return scheme.lower() == "bearer" and token == settings.api_key


class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if settings.auth_required and not is_public_path(request.url.path):
            if not credentials_match(request.headers.get("authorization")):
                return JSONResponse(
                    status_code=401,
                    content={
                        "code": "unauthorized",
                        "reason": "Missing or invalid API key",
                        "status": 401,
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return await call_next(request)


def dump_model(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value
