from typing import Annotated

from fastapi import APIRouter, Depends, Query
from openserp import AsyncOpenSERP

from app.auth import dump_model
from app.client import ENGINES, MEGA_MODES, get_client
from app.schemas import EngineName, ExtractMode, MegaMode

router = APIRouter(prefix="/api", tags=["search"])


def _search_kwargs(
    *,
    text: str,
    limit: int | None,
    region: str | None,
    lang: str | None,
    site: str | None,
    date: str | None,
    file: str | None,
    start: int | None,
    extract: int | None,
    extract_mode: ExtractMode | None,
) -> dict:
    params: dict = {"text": text}
    if limit is not None:
        params["limit"] = limit
    if region:
        params["region"] = region
    if lang:
        params["lang"] = lang
    if site:
        params["site"] = site
    if date:
        params["date"] = date
    if file:
        params["file"] = file
    if start is not None:
        params["start"] = start
    if extract:
        params["extract"] = extract
    if extract_mode:
        params["extract_mode"] = extract_mode
    return params


@router.get("/engines")
async def list_engines(client: AsyncOpenSERP = Depends(get_client)) -> dict:
    live = None
    try:
        live = dump_model(await client.engines())
    except Exception:  # noqa: BLE001 - static list is the contract
        live = None
    return {
        "engines": list(ENGINES),
        "modes": list(MEGA_MODES),
        "live": live,
    }


@router.get("/search")
async def search(
    client: AsyncOpenSERP = Depends(get_client),
    text: Annotated[str, Query(min_length=1)] = ...,
    engine: EngineName = "duckduckgo",
    limit: Annotated[int | None, Query(ge=1, le=100)] = 10,
    region: str | None = None,
    lang: str | None = None,
    site: str | None = None,
    date: str | None = None,
    file: str | None = None,
    start: Annotated[int | None, Query(ge=0)] = None,
    extract: Annotated[int | None, Query(ge=0, le=5)] = None,
    extract_mode: ExtractMode | None = None,
) -> dict:
    result = await client.search(
        engine=engine,
        **_search_kwargs(
            text=text,
            limit=limit,
            region=region,
            lang=lang,
            site=site,
            date=date,
            file=file,
            start=start,
            extract=extract,
            extract_mode=extract_mode,
        ),
    )
    return dump_model(result)


@router.get("/mega")
async def mega_search(
    client: AsyncOpenSERP = Depends(get_client),
    text: Annotated[str, Query(min_length=1)] = ...,
    engines: str | None = Query(
        default="duckduckgo,ecosia,bing",
        description="Comma-separated engine names",
    ),
    mode: MegaMode = "balanced",
    limit: Annotated[int | None, Query(ge=1, le=100)] = 10,
    region: str | None = None,
    lang: str | None = None,
    site: str | None = None,
    date: str | None = None,
    file: str | None = None,
    start: Annotated[int | None, Query(ge=0)] = None,
    extract: Annotated[int | None, Query(ge=0, le=5)] = None,
    extract_mode: ExtractMode | None = None,
) -> dict:
    engine_list = [item.strip() for item in (engines or "").split(",") if item.strip()]
    result = await client.mega_search(
        engines=engine_list or list(ENGINES),
        mode=mode,
        **_search_kwargs(
            text=text,
            limit=limit,
            region=region,
            lang=lang,
            site=site,
            date=date,
            file=file,
            start=start,
            extract=extract,
            extract_mode=extract_mode,
        ),
    )
    return dump_model(result)
