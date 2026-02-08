#!/bin/bash

echo "🔍 Hacker News + RSS Reader 状态检查"
echo "======================================"
echo ""

echo "📦 Pods 状态:"
kubectl get pods -n hackernews

echo ""
echo "🔧 Services:"
kubectl get svc -n hackernews

echo ""
echo "🌐 Ingress:"
kubectl get ingress -n hackernews

echo ""
echo "🔗 访问地址:"
echo "   主页面: http://hackernews.local"
echo "   API:    http://hackernews.local/api/"

echo ""
echo "📊 资源使用:"
kubectl top pods -n hackernews 2>/dev/null || echo "   (metrics-server 未安装)"

echo ""
echo "📝 日志查看命令:"
echo "  后端: kubectl logs -f deployment/backend -n hackernews"
echo "  前端: kubectl logs -f deployment/frontend -n hackernews"
echo "  Postgres: kubectl logs -f statefulset/postgres -n hackernews"
echo "  Redis: kubectl logs -f deployment/redis -n hackernews"
