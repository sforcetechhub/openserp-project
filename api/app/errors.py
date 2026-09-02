import logging
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openserp import CaptchaError, RateLimitError, SERPError, TimeoutError

from app.config import settings

logger = logging.getLogger("openserp-api")


def _payload(status: int, code: str, reason: str | None, request_id: str | None = None) -> dict[str, Any]:
    return {
        "code": code,
        "reason": reason or code,
        "status": status,
        "request_id": request_id,
    }


def _unreachable_payload(exc: BaseException) -> dict[str, Any]:
    return _payload(
        503,
        "openserp_unreachable",
        (
            f"Cannot reach OpenSERP at {settings.openserp_base_url}. "
            "On Railway add a second service from Docker image karust/openserp:latest "
            "named openserp, start command `serve -a 0.0.0.0 -p 7000`, "
            "then set OPENSERP_BASE_URL=http://openserp.railway.internal:7000. "
            f"Details: {exc}"
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RateLimitError)
    async def rate_limit_handler(_request: Request, exc: RateLimitError) -> JSONResponse:
        status = exc.status or 429
        return JSONResponse(
            status_code=status,
            content=_payload(status, str(exc.code or "rate_limited"), exc.reason, exc.request_id),
        )

    @app.exception_handler(CaptchaError)
    async def captcha_handler(_request: Request, exc: CaptchaError) -> JSONResponse:
        status = exc.status or 403
        return JSONResponse(
            status_code=status,
            content=_payload(status, str(exc.code or "captcha_detected"), exc.reason, exc.request_id),
        )

    @app.exception_handler(TimeoutError)
    async def timeout_handler(_request: Request, exc: TimeoutError) -> JSONResponse:
        status = exc.status or 504
        return JSONResponse(
            status_code=status,
            content=_payload(
                status,
                str(exc.code or "request_timeout"),
                exc.reason or str(exc),
                exc.request_id,
            ),
        )

    @app.exception_handler(SERPError)
    async def serp_handler(_request: Request, exc: SERPError) -> JSONResponse:
        status = exc.status or 502
        logger.warning("OpenSERP error %s: %s", status, exc)
        return JSONResponse(
            status_code=status,
            content=_payload(
                status,
                str(exc.code or "serp_error"),
                exc.reason or str(exc),
                exc.request_id,
            ),
        )

    @app.exception_handler(httpx.RequestError)
    async def httpx_handler(_request: Request, exc: httpx.RequestError) -> JSONResponse:
        logger.warning("OpenSERP transport error: %s", exc)
        return JSONResponse(status_code=503, content=_unreachable_payload(exc))

    @app.exception_handler(Exception)
    async def unhandled_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error")
        text = str(exc).lower()
        if any(
            token in text
            for token in (
                "connect",
                "name or service not known",
                "nodename nor servname",
                "getaddrinfo",
                "errno 111",
                "connection refused",
            )
        ):
            return JSONResponse(status_code=503, content=_unreachable_payload(exc))
        return JSONResponse(
            status_code=500,
            content=_payload(500, "internal_error", str(exc) or "Internal server error"),
        )
