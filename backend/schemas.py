from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GenerateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    shop_name: str = Field(..., min_length=1, max_length=80)
    shop_type: str = Field(..., min_length=1, max_length=80)
    campaign: str = Field(..., min_length=1, max_length=300)
    audience: str = Field(..., min_length=1, max_length=160)
    platform: str = Field(default="小红书", max_length=40)
    tone: str = Field(default="真实探店", max_length=80)
    selling_points: Optional[str] = Field(default="", max_length=500)
    model: Optional[str] = Field(default=None, max_length=80)


class Shot(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scene: str
    camera: str
    caption: str = Field(alias="copy")


class ContentPack(BaseModel):
    titles: List[str]
    note: str
    video_script: str
    shots: List[Shot]
    shooting_checklist: List[str]
    comment_replies: List[str]
    variants: List[str]
    conversion_hook: str
    cover_prompt: str
    koc_brief: str


class GenerateResponse(BaseModel):
    model: str
    pack: ContentPack


class ImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1600)
    model: Optional[str] = Field(default=None, max_length=80)
    size: str = Field(default="1024x1024", max_length=20)


class ImageResponse(BaseModel):
    model: str
    image_url: Optional[str] = None
    b64_json: Optional[str] = None


class AppConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    default_model: str
    image_model: str
    model_options: List[str]
    image_enabled: bool
    base_host: str
