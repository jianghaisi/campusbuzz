# CampusBuzz AI

CampusBuzz AI 是一个面向校园周边小商家的本地生活内容生成工具。它可以把一次门店活动、新品信息或产品图片，快速转化为小红书/抖音可发布的种草内容、短视频脚本、拍摄 brief 和封面图。

## 核心功能

- **内容包生成**：根据店铺名、店铺类型、活动、新品、目标人群和内容风格，生成完整种草内容包。
- **多平台内容适配**：适合小红书、抖音、本地生活团购、校园 KOC 探店等场景。
- **短视频脚本**：生成 30 秒短视频脚本，包含时间轴、画面安排和口播建议。
- **拍摄分镜**：输出门头、产品细节、制作过程、真人体验、价格权益等镜头规划。
- **KOC Brief**：自动整理给学生探店博主的拍摄需求，减少商家和博主反复沟通。
- **评论区回复**：生成适合种草内容的评论回复话术。
- **封面图提示词**：根据当前店铺和产品自动生成封面图 prompt。
- **AI 图片生成**：支持使用 `gpt-image-2` 生成小红书封面图。
- **上传图片改图**：支持上传奶茶、饭菜、饰品或其他产品图片，并基于提示词进行精修、场景化或商业质感增强。
- **提示词卡片**：内置三种图片提示词方案：
  - 精修种草封面
  - 商业质感大片
  - 真实探店增强
- **自定义提示词**：用户可以在内置模板基础上自由修改图片生成/改图要求。
- **品牌约束**：上传图片中如果包含无关品牌、店名、Logo 或包装文字，系统会提示模型删除或替换为当前店铺名。
- **历史记录**：浏览器本地保留最近生成的内容，方便回看和复用。
- **一键复制**：支持复制标题、笔记、脚本、KOC brief 和完整内容包。

## 适用场景

- 校园附近奶茶店、餐饮店、美甲店、饰品店、健身房、桌游店等小商家
- 想做小红书/抖音但缺少内容运营能力的本地商户
- 接商单的学生 KOC、探店博主、校园代运营团队
- 需要快速验证本地生活内容 AI 产品机会的创业项目

## 技术栈

- Frontend: React + Vite + Nginx
- Backend: FastAPI + httpx
- AI API: OpenAI-compatible API
- Deployment: Docker Compose

## 环境变量

复制 `.env.example` 为 `.env`，并填写模型中转站配置：

```env
AI_BASE_URL=https://your-relay.example.com/v1
AI_API_KEY=replace-with-your-relay-key
AI_MODEL=gpt-5.4-mini
IMAGE_MODEL=gpt-image-2
MODEL_OPTIONS=gpt-5.4-mini,gpt-5.4,gpt-5.2,gpt-5.3-codex
```

如果你使用的是历史兼容命名，也可以配置：

```env
RERANK_BASE_URL=https://your-relay.example.com/v1
RERANK_API_KEY=replace-with-your-relay-key
AI_MODEL=gpt-5.4-mini
IMAGE_MODEL=gpt-image-2
```

## Docker 一键部署

确保本机或服务器已安装 Docker 和 Docker Compose，然后在项目根目录执行：

```bash
docker compose up -d --build
```

默认访问地址：

```text
http://localhost:8080
```

后端健康检查：

```text
http://localhost:8000/api/health
```

如果 `8080` 端口被占用，可以在 `docker-compose.yml` 中修改前端端口：

```yaml
frontend:
  ports:
    - "8090:80"
```

然后重新启动：

```bash
docker compose up -d --build
```

## 常用命令

查看容器状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f
```

停止服务：

```bash
docker compose down
```

重新构建：

```bash
docker compose up -d --build
```

## 本地开发

后端：

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## 项目结构

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
├── docker-compose.yml
├── .env.example
└── README.md
```
