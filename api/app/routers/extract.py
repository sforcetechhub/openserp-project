from fastapi import APIRouter, Depends
from openserp import AsyncOpenSERP

from app.auth import dump_model
from app.client import get_client
from app.schemas import BatchExtractBody, ExtractBody

router = APIRouter(prefix="/api", tags=["extract"])


@router.post("/extract")
async def extract(body: ExtractBody, client: AsyncOpenSERP = Depends(get_client)) -> dict:
    result = await client.extract(
        url=str(body.url),
        mode=body.mode,
        min_runes=body.min_runes,
        clean=body.clean,
        use_llms_txt=body.use_llms_txt,
        region=body.region,
        lang=body.lang,
    )
    return dump_model(result)


@router.post("/extract/batch")
async def extract_batch(body: BatchExtractBody, client: AsyncOpenSERP = Depends(get_client)) -> dict:
    result = await client.batch_extract(
        urls=[str(url) for url in body.urls],
        mode=body.mode,
        min_runes=body.min_runes,
        clean=body.clean,
        use_llms_txt=body.use_llms_txt,
        region=body.region,
        lang=body.lang,
    )
    return dump_model(result)
