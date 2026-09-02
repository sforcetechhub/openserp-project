import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.auth import ApiKeyMiddleware
from app.client import lifespan
from app.config import settings
from app.errors import register_exception_handlers
from app.routers import extract, health, images, search

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="OpenSERP API",
    description="FastAPI wrapper around self-hosted OpenSERP using the official Python SDK.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(ApiKeyMiddleware)
register_exception_handlers(app)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(health.router)
app.include_router(search.router)
app.include_router(images.router)
app.include_router(extract.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"auth_required": settings.auth_required},
    )
