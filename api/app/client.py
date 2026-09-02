import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from openserp import AsyncOpenSERP

from app.config import settings

logger = logging.getLogger("openserp-api")

ENGINES = ("google", "bing", "duckduckgo", "yandex", "baidu", "ecosia")
MEGA_MODES = ("balanced", "fast", "any")


async def wait_for_openserp(client: AsyncOpenSERP) -> bool:
    """Retry OpenSERP /health so Railway deploys survive a slow Chromium boot."""
    last_error: Exception | None = None
    for attempt in range(1, settings.startup_retries + 1):
        try:
            await client.health()
            logger.info("OpenSERP is ready at %s", settings.openserp_base_url)
            return True
        except Exception as exc:  # noqa: BLE001 - any connect/health failure is retryable
            last_error = exc
            logger.warning(
                "Waiting for OpenSERP (%s/%s): %s",
                attempt,
                settings.startup_retries,
                exc,
            )
            await asyncio.sleep(settings.startup_retry_delay)
    logger.error("OpenSERP did not become ready: %s", last_error)
    return False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    client = AsyncOpenSERP(
        base_url=settings.openserp_base_url.rstrip("/"),
        backend="oss",
        timeout=settings.openserp_timeout,
    )
    app.state.client = client
    app.state.openserp_ready = await wait_for_openserp(client)
    try:
        yield
    finally:
        await client.close()


def get_client(request: Request) -> AsyncOpenSERP:
    return request.app.state.client
