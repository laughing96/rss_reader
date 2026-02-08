#!/bin/bash

set -e

echo "🚀 Hacker News + RSS Reader - 自动部署脚本"
echo "============================================"

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

# 检查 PVC 状态 (StatefulSet 的 PVC 变更需要特殊处理)
echo ""
echo "🔍 检查 PVC 状态..."
PVC_EXISTS=$(kubectl get pvc postgres-storage-postgres-0 -n hackernews 2>/dev/null || echo "")

if [ -n "$PVC_EXISTS" ]; then
    echo "✅ PVC 已存在"
    
    # 获取当前 PVC 的配置
    CURRENT_STORAGE=$(kubectl get pvc postgres-storage-postgres-0 -n hackernews -o jsonpath='{.spec.resources.requests.storage}' 2>/dev/null || echo "unknown")
    echo "   当前存储大小: $CURRENT_STORAGE"
    
    # 注意: StatefulSet 不允许直接修改 PVC 模板
    # 如果需要更改 PVC，必须先删除 StatefulSet 和 PVC，然后重新创建
    echo ""
    echo "⚠️  提示: 如需修改 PVC 存储大小，请运行 ./cleanup.sh 清理后重新部署"
else
    echo "ℹ️  PVC 不存在，将创建新的 PVC"
fi

# 检查并安装 ingress-nginx controller
echo ""
echo "🔍 检查 Ingress Controller..."
if ! kubectl get pods -n ingress-nginx 2>/dev/null | grep -q "controller"; then
    echo "📦 安装 nginx-ingress controller..."
    kubectl apply -f k8s/nginx.yaml
    
    echo "⏳ 等待 Ingress Controller 启动..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=120s
    echo "✅ Ingress Controller 已就绪"
else
    echo "✅ Ingress Controller 已存在"
fi

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

# 部署应用到 Kubernetes
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

# 自动配置 hosts (需要 sudo)
echo "📝 检查 hosts 配置..."
if ! grep -q "hackernews.local" /etc/hosts 2>/dev/null; then
    echo "⚙️  正在配置 hosts 文件..."
    if echo '127.0.0.1 hackernews.local' | sudo tee -a /etc/hosts > /dev/null; then
        echo "✅ hosts 配置已添加: hackernews.local -> 127.0.0.1"
    else
        echo "❌ hosts 配置失败，请手动添加:"
        echo "   echo '127.0.0.1 hackernews.local' | sudo tee -a /etc/hosts"
    fi
else
    echo "✅ hosts 配置已存在"
fi

# 等待 ingress 就绪
echo ""
echo "⏳ 等待 Ingress 就绪..."
sleep 2

# 显示 Ingress 状态
echo ""
echo "📊 Ingress 状态:"
kubectl get ingress -n hackernews

# 显示 Pod 状态
echo ""
echo "📊 Pod 状态:"
kubectl get pods -n hackernews

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址:"
echo "   http://hackernews.local"
echo ""
echo "📚 API 端点:"
echo "   http://hackernews.local/api/"
echo ""
echo "⚠️  重要提示:"
echo "   - PVC 数据会持久化保存"
echo "   - 如需完全重置数据，运行: ./cleanup.sh"
echo "   - 如需查看状态，运行: ./status.sh"
echo "=========================================="
