from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ai_client import edit_image, generate_content_pack, generate_image, get_ai_config, get_app_config
from schemas import AppConfig, GenerateRequest, GenerateResponse, ImageRequest, ImageResponse


app = FastAPI(title="CampusBuzz AI API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    config = get_ai_config()
    return {
        "ok": True,
        "ai_base_url_configured": bool(config["base_url"]),
        "ai_key_configured": bool(config["api_key"]),
        "model": config["model"],
        "image_model": config["image_model"],
    }


@app.get("/api/config", response_model=AppConfig)
async def app_config():
    return get_app_config()


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest):
    try:
        return await generate_content_pack(payload)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {exc}") from exc


@app.post("/api/generate-image", response_model=ImageResponse)
async def image(payload: ImageRequest):
    try:
        return await generate_image(payload)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Image generation failed: {exc}") from exc


@app.post("/api/edit-image", response_model=ImageResponse)
async def image_edit(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    model: str = Form(default="gpt-image-2"),
    size: str = Form(default="1024x1024"),
):
    try:
        image_bytes = await image.read()
        return await edit_image(
            image_bytes=image_bytes,
            filename=image.filename or "upload.png",
            content_type=image.content_type or "image/png",
            prompt=prompt,
            model=model,
            size=size,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Image edit failed: {exc}") from exc
