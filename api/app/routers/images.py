from typing import Annotated

from fastapi import APIRouter, Depends, Query
from openserp import AsyncOpenSERP

from app.auth import dump_model
from app.client import ENGINES, get_client
from app.schemas import EngineName, MegaMode

router = APIRouter(prefix="/api", tags=["images"])


@router.get("/images")
async def images(
    client: AsyncOpenSERP = Depends(get_client),
    text: Annotated[str, Query(min_length=1)] = ...,
    engine: EngineName = "bing",
    engines: str | None = Query(
        default=None,
        description="Comma-separated engines; when set, runs mega image search",
    ),
    mode: MegaMode = "balanced",
    limit: Annotated[int | None, Query(ge=1, le=100)] = 10,
    region: str | None = None,
    lang: str | None = None,
) -> dict:
    params: dict = {"text": text}
    if limit is not None:
        params["limit"] = limit
    if region:
        params["region"] = region
    if lang:
        params["lang"] = lang

    engine_list = [item.strip() for item in (engines or "").split(",") if item.strip()]
    if engine_list:
        result = await client.mega_image(engines=engine_list or list(ENGINES), mode=mode, **params)
    else:
        result = await client.image(engine=engine, **params)
    return dump_model(result)
