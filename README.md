# 🚀 Hacker News + RSS Reader

一个本地运行的 Hacker News 和 RSS 阅读器，使用 Vue3 + FastAPI + PostgreSQL + Redis，通过 Kubernetes 在 Orbstack 上部署。

## 📁 项目结构

```
hackernews-reader/
├── backend/                 # FastAPI 后端
│   ├── main.py             # API 入口
│   ├── database.py         # 数据库模型
│   ├── schemas.py          # Pydantic 模型
│   ├── services.py         # 业务逻辑
│   ├── requirements.txt    # Python 依赖
│   └── Dockerfile
├── frontend/               # Vue3 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── k8s/                    # Kubernetes 配置文件
│   ├── 00-namespace.yaml
│   ├── 01-postgres.yaml
│   ├── 02-redis.yaml
│   ├── 03-backend.yaml
│   ├── 04-frontend.yaml
│   └── 05-ingress.yaml
├── deploy.sh               # 一键部署脚本
├── cleanup.sh              # 清理脚本
├── status.sh               # 状态检查脚本
└── README.md
```

## 🏗️ 技术栈

- **前端**: Vue 3 + Vite + Pinia + Vue Router + Axios
- **后端**: FastAPI + SQLAlchemy + Pydantic
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **部署**: Kubernetes + Docker

## ✨ 功能特性

- 📰 实时获取 Hacker News 热门文章
- 📡 支持添加/删除 RSS Feed
- 🔄 自动刷新 RSS 内容
- 💾 Redis 缓存提高性能
- 🎨 响应式 UI 设计
- 🐳 完整 Kubernetes 部署

## 🚀 快速开始

### 前置要求

1. 安装 [Orbstack](https://orbstack.dev/) 并启用 Kubernetes
2. 确保 kubectl 可以连接集群

### 一键部署

```bash
cd hackernews-reader
./deploy.sh
```

### 访问应用

#### 方式 1: 使用 Ingress (推荐)

1. 安装 Ingress Controller:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

2. 添加 hosts:
```bash
echo '127.0.0.1 hackernews.local' | sudo tee -a /etc/hosts
```

3. 访问: http://hackernews.local

#### 方式 2: 使用端口转发

```bash
# 端口转发
kubectl port-forward svc/frontend 8080:80 -n hackernews &
kubectl port-forward svc/backend 8000:8000 -n hackernews &

# 访问
open http://localhost:8080
```

## 📋 API 端点

| 端点 | 描述 |
|------|------|
| `GET /` | API 信息 |
| `GET /health` | 健康检查 |
| `GET /api/hn/stories` | Hacker News 热门文章 |
| `GET /api/rss/feeds` | RSS Feed 列表 |
| `POST /api/rss/feeds` | 添加 RSS Feed |
| `DELETE /api/rss/feeds/{id}` | 删除 RSS Feed |
| `GET /api/rss/items` | RSS 文章列表 |
| `POST /api/rss/feeds/{id}/refresh` | 刷新 RSS Feed |
| `GET /api/combined` | 合并的 HN + RSS |

## 🔧 本地开发

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

## 📊 查看状态

```bash
./status.sh
```

## 🧹 清理资源

```bash
./cleanup.sh
```

## 🐛 故障排查

### 查看日志

```bash
# 后端日志
kubectl logs -f deployment/backend -n hackernews

# 前端日志
kubectl logs -f deployment/frontend -n hackernews

# PostgreSQL 日志
kubectl logs -f statefulset/postgres -n hackernews

# Redis 日志
kubectl logs -f deployment/redis -n hackernews
```

### 常见问题

**Pod 一直 Pending**
- 检查 PVC 是否绑定: `kubectl get pvc -n hackernews`
- Orbstack 可能需要手动创建存储

**镜像加载失败**
- 使用 `orbctl k8s load-image` 加载镜像
- 或手动导入: `docker save | kubectl exec ...`

**数据库连接失败**
- 等待 PostgreSQL 完全启动
- 检查 Service 名称是否正确

## 📄 License

MIT
