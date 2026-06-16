import asyncio
import json

from ai_client import generate_content_pack, get_app_config
from schemas import GenerateRequest


async def main() -> None:
    config = get_app_config()
    payload = GenerateRequest(
        shop_name="星河奶茶",
        shop_type="奶茶店",
        campaign="新品芋泥麻薯奶茶，第二杯半价",
        audience="大学生、女生、下午茶搭子",
        platform="小红书",
        tone="真实探店",
        selling_points="学校东门步行5分钟，有自习座位，拍照灯光好",
        model="gpt-5.4-mini",
    )
    result = await generate_content_pack(payload)
    pack = result["pack"]
    print(
        json.dumps(
            {
                "ok": True,
                "model": result["model"],
                "base_host": config["base_host"],
                "title_count": len(pack.titles),
                "shot_count": len(pack.shots),
                "has_cover_prompt": bool(pack.cover_prompt),
                "has_koc_brief": bool(pack.koc_brief),
                "first_title": pack.titles[0],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
