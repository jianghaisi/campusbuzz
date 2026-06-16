import json
import os
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv

from schemas import ContentPack, GenerateRequest, ImageRequest


load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


DEFAULT_MODELS = ["gpt-5.4-mini", "gpt-5.4", "gpt-5.2", "gpt-5.3-codex"]


def _env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value and not _is_placeholder(value):
            return value
    return default


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in {
        "your-openai-api-key-here",
        "your-api-key-here",
        "replace-with-your-relay-key",
        "sk-xxx",
        "sk-placeholder",
        "placeholder",
    }


def _normalize_model(model: str) -> str:
    aliases = {
        "gpt5.4.mini": "gpt-5.4-mini",
        "gpt-5.4.mini": "gpt-5.4-mini",
        "gpt5-4-mini": "gpt-5.4-mini",
        "gptimage2": "gpt-image-2",
        "gpt-image2": "gpt-image-2",
    }
    return aliases.get(model.strip().lower(), model.strip())


def get_ai_config(model_override: Optional[str] = None) -> Dict[str, str]:
    api_key = _env("AI_API_KEY", "OPENAI_API_KEY")
    using_relay_fallback = False
    if api_key:
        base_url = _env("AI_BASE_URL", "OPENAI_BASE_URL", default="https://api.openai.com/v1")
    else:
        using_relay_fallback = True
        api_key = _env("RERANK_API_KEY")
        base_url = _env("RERANK_BASE_URL", default="https://api.openai.com/v1")

    model = _normalize_model(model_override or _env("AI_MODEL", "OPENAI_MODEL", default="gpt-5.4-mini"))
    if using_relay_fallback and model in {"gpt-4", "gpt4"}:
        model = "gpt-5.4-mini"

    return {
        "base_url": base_url.rstrip("/"),
        "api_key": api_key,
        "model": model,
        "image_model": _normalize_model(_env("IMAGE_MODEL", default="gpt-image-2")),
    }


def get_app_config() -> Dict[str, Any]:
    config = get_ai_config()
    raw_options = _env("MODEL_OPTIONS")
    model_options = [_normalize_model(item) for item in raw_options.split(",") if item.strip()] if raw_options else DEFAULT_MODELS
    host = urlparse(config["base_url"]).netloc or config["base_url"]
    return {
        "default_model": config["model"],
        "image_model": config["image_model"],
        "model_options": model_options,
        "image_enabled": bool(config["api_key"]),
        "base_host": host,
    }


SYSTEM_PROMPT = """
你是 CampusBuzz AI，一名非常懂校园周边本地生活的小红书/抖音内容运营。
请只返回合法 JSON，不要 Markdown，不要解释。
内容要具体、可执行、像真实学生或探店博主会发的内容，避免空泛广告腔。

JSON schema:
{
  "titles": ["5 个小红书/抖音标题"],
  "note": "一篇 220-360 字可发布种草笔记",
  "video_script": "30 秒短视频脚本，带时间轴",
  "shots": [{"scene":"画面场景", "camera":"拍法", "copy":"画面字幕/口播"}],
  "shooting_checklist": ["6 个具体拍摄素材"],
  "comment_replies": ["5 条评论区回复话术"],
  "variants": ["3 个不同内容角度"],
  "conversion_hook": "一句到店/团购转化话术",
  "cover_prompt": "用于生成小红书封面图或改图的中文图片提示词，必须包含当前店铺名，必须适配当前店铺类型和产品，不要固定写奶茶，不得出现无关品牌",
  "koc_brief": "发给学生 KOC 的拍摄 brief，120 字以内"
}
""".strip()


def _user_prompt(payload: GenerateRequest) -> str:
    return f"""
店名：{payload.shop_name}
店铺类型：{payload.shop_type}
活动/新品：{payload.campaign}
目标人群：{payload.audience}
平台：{payload.platform}
风格：{payload.tone}
卖点补充：{payload.selling_points or "无"}

请生成一个校园本地生活种草内容包。内容必须具体到镜头、话术、拍摄素材和到店转化。
如果产品不是饮品，请根据真实品类生成对应措辞，例如饭菜强调热气、摆盘、食材和份量；小饰品强调材质、佩戴场景、细节光泽和搭配。
""".strip()


def _fallback_pack(payload: GenerateRequest) -> ContentPack:
    base = f"{payload.shop_name}{payload.campaign}"
    return ContentPack(
        titles=[
            f"学校附近这家{payload.shop_type}，新品真的有点会",
            f"{payload.audience}别错过：{base}",
            f"下课后冲这家店，活动太适合约朋友",
            f"不是广告，{payload.shop_name}这波活动我愿意推荐",
            f"校园周边省钱攻略：{payload.campaign}",
        ],
        note=(
            f"今天发现{payload.shop_name}在做{payload.campaign}，很适合{payload.audience}。"
            f"拍摄时建议先拍门头，再拍主推产品细节、制作或陈列过程、真实体验和价格权益。"
            "文案重点放在真实感、到店理由和适合谁，不要写得像硬广。"
        ),
        video_script=(
            "0-3s 门头和活动牌入镜；3-10s 展示主推产品细节；10-20s 真实体验或使用场景；"
            "20-27s 对比价格、份量或质感；27-30s 给出到店提示。"
        ),
        shots=[
            {"scene": "门头+活动牌", "camera": "手机竖屏推进", "copy": "下课路过看到这个活动"},
            {"scene": "产品细节", "camera": "近景拍材质、摆盘或包装", "copy": "这个细节比照片里还好看"},
            {"scene": "真实体验", "camera": "半身自然光", "copy": "适合和朋友一起冲"},
        ],
        shooting_checklist=["门头", "价格牌", "主推产品近景", "制作/陈列过程", "真人体验", "付款或团购入口"],
        comment_replies=["地址在学校附近，步行就能到", "活动时间建议先问店员", "可以先收藏，约朋友一起去", "人多时建议错峰去", "截图笔记到店更方便沟通"],
        variants=["学生党省钱版", "朋友结伴版", "约会/送礼版"],
        conversion_hook="到店报暗号或截图笔记，可优先领取活动权益。",
        cover_prompt=build_image_prompt(
            "polished_cover",
            payload.shop_type,
            payload.campaign,
            payload.selling_points or "",
            payload.shop_name,
        ),
        koc_brief=f"拍{payload.shop_name}门头、主推产品、细节、真实体验和价格权益，突出{payload.campaign}。",
    )


IMAGE_PROMPT_PRESETS = {
    "polished_cover": {
        "title": "精修种草封面",
        "description": "保留主体真实样子，提升光线、构图、质感，适合小红书首图。",
        "prompt": (
            "请基于上传图片中的主体进行精修，不要改变主体品类和核心外观。"
            "必须移除或替换原图中所有无关品牌、店名、Logo、杯身文字、包装文字和背景招牌；如果需要出现品牌文字，只能使用当前店铺名。"
            "根据主体类型自动优化：食物突出热气、色泽、摆盘和食欲；饮品突出杯身冷凝水、层次和清爽感；"
            "饰品突出材质、光泽、细节和佩戴/陈列氛围；其他商品突出真实质感和使用场景。"
            "画面适合小红书封面，明亮自然光，干净背景，有生活方式氛围，保留中文标题留白，不要夸张广告风。"
        ),
    },
    "commercial_scene": {
        "title": "商业质感大片",
        "description": "更像商家宣传图，适合团购页、海报和活动页。",
        "prompt": (
            "请把上传图片中的主体做成高质感商业宣传图。主体必须仍然是原图里的物件，不要换成其他品类。"
            "必须移除或替换原图中所有无关品牌、店名、Logo、杯身文字、包装文字和背景招牌；如果需要出现品牌文字，只能使用当前店铺名。"
            "根据品类自动选择合适场景：饭菜使用温暖餐桌和诱人摆盘；饮品使用清爽桌面和自然光；"
            "小饰品使用柔和布景、微距细节和高级光泽；其他物件使用简洁陈列和品牌感背景。"
            "要求画面精致、真实、可用于本地生活商家推广。"
        ),
    },
    "real_life_upgrade": {
        "title": "真实探店增强",
        "description": "更像学生实拍，但比原图更干净、更好看。",
        "prompt": (
            "请在保留上传图片真实探店感的基础上优化画面。不要过度商业化，不要改变主体是什么。"
            "必须移除或替换原图中所有无关品牌、店名、Logo、杯身文字、包装文字和背景招牌；如果需要出现品牌文字，只能使用当前店铺名。"
            "根据主体自动处理：饭菜保留烟火气和份量感；饮品保留手持/桌面真实感；饰品保留细节和搭配感；"
            "其他物件保留真实使用场景。提升亮度、清晰度、构图和背景整洁度，让它像学生博主会发布的小红书图片。"
        ),
    },
}


def build_image_prompt(preset: str, shop_type: str, campaign: str, extra: str = "", shop_name: str = "") -> str:
    preset_prompt = IMAGE_PROMPT_PRESETS.get(preset, IMAGE_PROMPT_PRESETS["polished_cover"])["prompt"]
    brand_rule = (
        f"当前店铺名：{shop_name or '当前店铺'}。"
        "成品图中不得出现任何无关品牌、店名、Logo、杯身文字、包装文字或背景招牌。"
        f"若上传图里有其他品牌，必须删除或替换为“{shop_name or '当前店铺名'}”；如果文字渲染不稳定，宁可使用无字干净包装，也不要保留错误品牌。"
    )
    context = f"店铺类型：{shop_type}。活动/产品：{campaign}。补充信息：{extra or '无'}。"
    return f"{context}\n{brand_rule}\n{preset_prompt}"


def _extract_json(content: str) -> Dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            return json.loads(content[start : end + 1])
        raise


async def _post_json(path: str, body: Dict[str, Any], config: Dict[str, str]) -> Dict[str, Any]:
    if not config["api_key"]:
        raise RuntimeError("Missing API key. Set AI_API_KEY or RERANK_API_KEY.")

    headers = {"Authorization": f"Bearer {config['api_key']}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=120, trust_env=True) as client:
        response = await client.post(f"{config['base_url']}{path}", headers=headers, json=body)
        response.raise_for_status()
        return response.json()


async def _post_multipart(path: str, data: Dict[str, str], files: Dict[str, Any], config: Dict[str, str]) -> Dict[str, Any]:
    if not config["api_key"]:
        raise RuntimeError("Missing API key. Set AI_API_KEY or RERANK_API_KEY.")

    headers = {"Authorization": f"Bearer {config['api_key']}"}
    async with httpx.AsyncClient(timeout=180, trust_env=True) as client:
        response = await client.post(f"{config['base_url']}{path}", headers=headers, data=data, files=files)
        response.raise_for_status()
        return response.json()


async def generate_content_pack(payload: GenerateRequest) -> Dict[str, Any]:
    config = get_ai_config(payload.model)
    request_body = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _user_prompt(payload)},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    data = await _post_json("/chat/completions", request_body, config)
    content = data["choices"][0]["message"]["content"]
    try:
        pack = ContentPack.model_validate(_extract_json(content))
    except Exception:
        pack = _fallback_pack(payload)

    return {"model": config["model"], "pack": pack}


async def generate_image(payload: ImageRequest) -> Dict[str, Any]:
    config = get_ai_config()
    image_model = _normalize_model(payload.model or config["image_model"])
    request_body = {
        "model": image_model,
        "prompt": payload.prompt,
        "size": payload.size,
        "n": 1,
    }

    data = await _post_json("/images/generations", request_body, config)
    first = (data.get("data") or [{}])[0]
    return {
        "model": image_model,
        "image_url": first.get("url"),
        "b64_json": first.get("b64_json"),
    }


async def edit_image(image_bytes: bytes, filename: str, content_type: str, prompt: str, model: Optional[str], size: str) -> Dict[str, Any]:
    config = get_ai_config()
    image_model = _normalize_model(model or config["image_model"])
    data = {
        "model": image_model,
        "prompt": prompt,
        "size": size,
        "n": "1",
    }
    files = {
        "image": (filename or "upload.png", image_bytes, content_type or "image/png"),
    }

    response = await _post_multipart("/images/edits", data, files, config)
    first = (response.get("data") or [{}])[0]
    return {
        "model": image_model,
        "image_url": first.get("url"),
        "b64_json": first.get("b64_json"),
    }
