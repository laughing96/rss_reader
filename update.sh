#!/bin/bash

set -e

echo "🔄 Hacker News + RSS Reader - 更新脚本"
echo "======================================="

# Check what to update
UPDATE_BACKEND=false
UPDATE_FRONTEND=false

if [ "$1" == "backend" ] || [ "$1" == "all" ]; then
    UPDATE_BACKEND=true
fi

if [ "$1" == "frontend" ] || [ "$1" == "all" ]; then
    UPDATE_FRONTEND=true
fi

if [ "$1" == "" ]; then
    echo "用法: ./update.sh [backend|frontend|all]"
    echo ""
    echo "示例:"
    echo "  ./update.sh backend   - 只更新后端"
    echo "  ./update.sh frontend  - 只更新前端"
    echo "  ./update.sh all       - 更新前后端"
    exit 1
fi

# Check kubectl
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes 集群未运行"
    exit 1
fi

echo "✅ Kubernetes 集群已就绪"
echo ""

# Update backend
if [ "$UPDATE_BACKEND" = true ]; then
    echo "📦 更新后端..."
    echo "构建后端镜像..."
    cd backend
    docker build -t hackernews-reader-backend:latest .
    cd ..
    
    echo "重启后端 Deployment..."
    kubectl rollout restart deployment/backend -n hackernews
    kubectl rollout status deployment/backend -n hackernews --timeout=120s
    echo "✅ 后端更新完成"
    echo ""
fi

# Update frontend
if [ "$UPDATE_FRONTEND" = true ]; then
    echo "📦 更新前端..."
    echo "构建前端镜像..."
    cd frontend
    docker build -t hackernews-reader-frontend:latest .
    cd ..
    
    echo "重启前端 Deployment..."
    kubectl rollout restart deployment/frontend -n hackernews
    kubectl rollout status deployment/frontend -n hackernews --timeout=120s
    echo "✅ 前端更新完成"
    echo ""
fi

echo "🎉 更新完成！"
echo ""
echo "📊 Pod 状态:"
kubectl get pods -n hackernews
