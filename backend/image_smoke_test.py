import asyncio
import base64
import json
from pathlib import Path

from ai_client import generate_image, get_app_config
from schemas import ImageRequest


async def main() -> None:
    config = get_app_config()
    result = await generate_image(
        ImageRequest(
            model=config["image_model"],
            size="1024x1024",
            prompt=(
                "小红书封面图，校园奶茶店新品芋泥麻薯奶茶，真实探店感，"
                "明亮自然光，桌面有奶茶和学生书本，中文标题留白，不要夸张广告风"
            ),
        )
    )
    output_path = Path(__file__).with_name("image_smoke_output.png")
    if result.get("b64_json"):
        output_path.write_bytes(base64.b64decode(result["b64_json"]))
    print(
        json.dumps(
            {
                "ok": bool(result.get("image_url") or result.get("b64_json")),
                "model": result["model"],
                "has_url": bool(result.get("image_url")),
                "b64_length": len(result.get("b64_json") or ""),
                "saved_to": str(output_path) if output_path.exists() else "",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
