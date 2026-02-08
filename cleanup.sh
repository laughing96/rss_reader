#!/bin/bash

echo "🧹 清理 Hacker News + RSS Reader 资源..."
echo ""

# 删除 PVC (StatefulSet 创建的 PVC 不会随 namespace 删除而删除)
echo "🗑️  删除 PVC..."
kubectl delete pvc postgres-storage-postgres-0 -n hackernews || echo "   PVC 不存在或已删除"

# 删除 namespace (这会删除所有其他资源)
echo "🗑️  删除 Namespace..."
kubectl delete namespace hackernews

echo ""
echo "✅ 清理完成"
echo ""
echo "如需删除镜像，请运行:"
echo "  docker rmi hackernews-reader-backend:latest"
echo "  docker rmi hackernews-reader-frontend:latest"
