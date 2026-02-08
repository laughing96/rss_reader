#!/bin/bash

echo "🧹 清理 Hacker News + RSS Reader 资源..."

kubectl delete namespace hackernews

echo "✅ 清理完成"
echo ""
echo "如需删除镜像，请运行:"
echo "  docker rmi hackernews-reader-backend:latest"
echo "  docker rmi hackernews-reader-frontend:latest"
