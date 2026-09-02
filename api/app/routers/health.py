from fastapi import APIRouter, Depends, Request
from openserp import AsyncOpenSERP, OssOnlyError

from app.auth import dump_model
from app.client import get_client
from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(request: Request, client: AsyncOpenSERP = Depends(get_client)) -> dict:
    openserp: dict | None = None
    ready = bool(getattr(request.app.state, "openserp_ready", False))
    try:
        status = await client.health()
        openserp = dump_model(status)
        ready = True
        request.app.state.openserp_ready = True
    except OssOnlyError as exc:
        openserp = {"error": str(exc)}
        ready = False
    except Exception as exc:  # noqa: BLE001
        openserp = {"error": str(exc)}
        ready = False
        request.app.state.openserp_ready = False

    return {
        "status": "ok" if ready else "degraded",
        "openserp_ready": ready,
        "openserp_base_url": settings.resolved_openserp_base_url,
        "openserp": openserp,
    }
