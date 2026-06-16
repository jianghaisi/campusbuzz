<div align="center">


# 校园周边小商家的本地生活内容 AI Copilot--CampusBuzz AI

把一次门店活动、新品信息或产品图片，快速转化为小红书/抖音可发布的种草内容、短视频脚本、拍摄 brief 和封面图。

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=111)
![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=fff)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=fff)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=fff)
![AI](https://img.shields.io/badge/AI-gpt--5.4--mini%20%7C%20gpt--image--2-black)

</div>

## Preview

### Content Workbench

![CampusBuzz AI content workbench](docs/images/content-workbench.png)

### Generated Content + Cover Workflow

![CampusBuzz AI workspace results](docs/images/workspace-results.png)

### AI Generated Cover

![AI generated cover for Xinghe Milk Tea](docs/images/generated-cover.png)

## What It Does

CampusBuzz AI is designed for campus-area local businesses that need short-form content but do not have a dedicated content team.

It helps merchants turn a simple activity brief into a full publishing package:

- Xiaohongshu / Douyin titles
- Publish-ready seed content note
- 30-second short-video script
- Shot-by-shot filming plan
- KOC shooting brief
- Comment reply templates
- Store-visit conversion copy
- Cover image prompt
- AI-generated or AI-edited cover image

## Key Features

| Feature                 | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| Content Pack Generation | Generate a complete local-life content package from shop, activity, audience, platform, and tone. |
| Short Video Script      | Create a 30-second video script with timeline, camera direction, and on-screen copy. |
| Shot List               | Generate practical filming shots such as storefront, product close-up, preparation process, real experience, and deal display. |
| KOC Brief               | Create a concise brief for student KOCs or campus creators.  |
| Image Generation        | Use `gpt-image-2` to generate Xiaohongshu-style cover images. |
| Image Editing           | Upload product photos and improve them with AI image editing. |
| Prompt Presets          | Choose from polished cover, commercial scene, or real-life creator style. |
| Brand Guardrails        | Remove unrelated brand names, logos, packaging text, and replace them with the current shop name when needed. |
| Copy Buttons            | Copy titles, note, script, brief, and full content package with one click. |
| Local History           | Keep recent generations in browser local storage for quick reuse. |

## Image Prompt Presets

CampusBuzz AI includes three image prompt cards:

1. **精修种草封面**  
   Keeps the product realistic while improving lighting, composition, and texture for Xiaohongshu covers.

2. **商业质感大片**  
   Turns uploaded product images into polished commercial-style visuals for campaigns and group-buy pages.

3. **真实探店增强**  
   Preserves the student creator / real visit feeling while making the image cleaner and more publishable.

Users can also write custom prompts. The app automatically injects shop context and brand constraints, so uploaded photos containing unrelated brands such as other milk-tea chains can be cleaned or replaced with the current shop name.

## Use Cases

- Milk tea shops, restaurants, accessory shops, beauty salons, gyms, board-game stores, and other small shops around campus
- Local businesses that want to publish on Xiaohongshu or Douyin but lack content operation experience
- Student KOCs and campus creators who need faster merchant brief generation
- Early-stage AI startup opportunity validation for local-life content workflows

## Tech Stack

- **Frontend**: React, Vite, lucide-react, Nginx
- **Backend**: FastAPI, httpx, Pydantic
- **AI API**: OpenAI-compatible relay API
- **Deployment**: Docker Compose

## Environment Variables

Copy `.env.example` to `.env` and configure your API relay:

```env
AI_BASE_URL=https://your-relay.example.com/v1
AI_API_KEY=replace-with-your-relay-key
AI_MODEL=gpt-5.4-mini
IMAGE_MODEL=gpt-image-2
MODEL_OPTIONS=gpt-5.4-mini,gpt-5.4,gpt-5.2,gpt-5.3-codex
```

Historical compatible naming is also supported:

```env
RERANK_BASE_URL=https://your-relay.example.com/v1
RERANK_API_KEY=replace-with-your-relay-key
AI_MODEL=gpt-5.4-mini
IMAGE_MODEL=gpt-image-2
```

## Docker One-Command Deployment

Make sure Docker and Docker Compose are installed, then run:

```bash
docker compose up -d --build
```

Default URLs:

```text
Frontend: http://localhost:8080
Backend health check: http://localhost:8000/api/health
```

If port `8080` is already in use, edit `docker-compose.yml`:

```yaml
frontend:
  ports:
    - "8090:80"
```

Then rebuild:

```bash
docker compose up -d --build
```

## Common Commands

```bash
# Show containers
docker compose ps

# Follow logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild and restart
docker compose up -d --build
```

## Local Development

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```text
.
├── backend
│   ├── ai_client.py
│   ├── main.py
│   ├── requirements.txt
│   └── schemas.py
├── frontend
│   ├── src
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docs
│   └── images
├── docker-compose.yml
├── .env.example
└── README.md
```

## Notes

Image generation and image editing may take longer than text generation. The frontend Nginx config includes longer proxy timeouts and a larger upload limit for image workflows.
