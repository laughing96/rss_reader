#!/bin/bash

set -e

echo "🚀 Hacker News + RSS Reader - Kubernetes 部署脚本"
echo "=================================================="

# 检查 Orbstack 和 kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl 未安装，请先安装 kubectl"
    exit 1
fi

if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes 集群未运行，请启动 Orbstack Kubernetes"
    exit 1
fi

echo "✅ Kubernetes 集群已就绪"

# 构建镜像
echo ""
echo "📦 构建 Docker 镜像..."

# 构建后端镜像
echo "构建后端镜像..."
cd backend
docker build -t hackernews-reader-backend:latest .
cd ..

# 构建前端镜像
echo "构建前端镜像..."
cd frontend
docker build -t hackernews-reader-frontend:latest .
cd ..

# 镜像已构建，Orbstack/macOS Docker Desktop 会自动共享镜像给 Kubernetes
echo ""
echo "✅ Docker 镜像已准备就绪"

# 部署到 Kubernetes
echo ""
echo "🎯 部署应用到 Kubernetes..."
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-postgres.yaml
kubectl apply -f k8s/02-redis.yaml
kubectl apply -f k8s/03-backend.yaml
kubectl apply -f k8s/04-frontend.yaml
kubectl apply -f k8s/05-ingress.yaml

# 等待部署完成
echo ""
echo "⏳ 等待服务启动..."
kubectl wait --for=condition=ready pod -l app=postgres -n hackernews --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n hackernews --timeout=120s
kubectl wait --for=condition=ready pod -l app=backend -n hackernews --timeout=120s
kubectl wait --for=condition=ready pod -l app=frontend -n hackernews --timeout=120s

echo ""
echo "✨ 部署完成！"
echo ""
echo "📋 访问方式:"
echo "   1. 添加 hosts: echo '127.0.0.1 hackernews.local' | sudo tee -a /etc/hosts"
echo "   2. 启用 Ingress: kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml"
echo "   3. 或者使用端口转发:"
echo "      - 前端: kubectl port-forward svc/frontend 8080:80 -n hackernews"
echo "      - 后端: kubectl port-forward svc/backend 8000:8000 -n hackernews"
echo ""
echo "🌐 访问地址:"
echo "   - 如果配置了 Ingress: http://hackernews.local"
echo "   - 如果使用端口转发: http://localhost:8080"
echo ""

# 显示 Pod 状态
echo "📊 Pod 状态:"
kubectl get pods -n hackernews
