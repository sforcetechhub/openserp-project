import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openserp import CaptchaError, RateLimitError, SERPError, TimeoutError

logger = logging.getLogger("openserp-api")


def _payload(status: int, code: str, reason: str | None, request_id: str | None = None) -> dict[str, Any]:
    return {
        "code": code,
        "reason": reason or code,
        "status": status,
        "request_id": request_id,
    }


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
            content=_payload(status, str(exc.code or "request_timeout"), exc.reason or str(exc), exc.request_id),
        )

    @app.exception_handler(SERPError)
    async def serp_handler(_request: Request, exc: SERPError) -> JSONResponse:
        status = exc.status or 502
        logger.warning("OpenSERP error %s: %s", status, exc)
        return JSONResponse(
            status_code=status,
            content=_payload(status, str(exc.code or "serp_error"), exc.reason or str(exc), exc.request_id),
        )
