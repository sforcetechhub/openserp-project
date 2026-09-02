from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

EngineName = Literal["google", "bing", "duckduckgo", "yandex", "baidu", "ecosia"]
MegaMode = Literal["balanced", "fast", "any"]
ExtractMode = Literal["auto", "fast", "rendered"]


class ExtractBody(BaseModel):
    url: HttpUrl
    mode: ExtractMode | None = None
    min_runes: int | None = Field(default=None, ge=0)
    clean: bool | None = True
    use_llms_txt: bool | None = None
    region: str | None = None
    lang: str | None = None


class BatchExtractBody(BaseModel):
    urls: list[HttpUrl] = Field(min_length=1, max_length=20)
    mode: ExtractMode | None = None
    min_runes: int | None = Field(default=None, ge=0)
    clean: bool | None = True
    use_llms_txt: bool | None = None
    region: str | None = None
    lang: str | None = None
