#!/bin/bash

echo "🔄 Hacker News + RSS Reader - 完全重置"
echo "========================================"
echo ""
echo "⚠️  警告: 这将删除所有数据包括数据库！"
echo ""

# 确认操作
read -p "确定要继续吗? (输入 'yes' 确认): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ 已取消"
    exit 0
fi

read -p "原始数据库也要删除么 (输入 'yes' 确认): " rmdb


echo ""
echo "🗑️  正在清理所有资源..."

# 删除 ingress (可选，如果不删 namespace 会处理)
kubectl delete ingress hackernews-ingress -n hackernews 2>/dev/null || true

# 按顺序删除 StatefulSet (这会保留 PVC)
echo "   删除 PostgreSQL StatefulSet..."
kubectl delete statefulset postgres -n hackernews 2>/dev/null || true

# 等待 StatefulSet 删除完成 (确保 Pod 先终止)
sleep 5

# 删除 PVC (这是关键！StatefulSet 的 PVC 不会自动删除)
echo "   删除 PVC..."
kubectl delete pvc postgres-storage-postgres-0 -n hackernews 2>/dev/null || echo "   PVC 不存在或已删除"

# 删除 PV (如果 reclaim policy 是 Retain)
echo "   删除 PV..."
kubectl delete pv postgres-pv 2>/dev/null || echo "   PV 不存在或已删除"

# 删除 namespace (这会删除所有剩余资源)
echo "   删除 Namespace..."
kubectl delete namespace hackernews

# 清理本地数据目录
echo ""
if [ "$rmdb" == "yes" ]; then
    echo "🧹 清理本地数据目录..."
    if [ -d "./orbstack-pv/postgres" ]; then
        echo "   删除本地 PostgreSQL 数据..."
        rm -rf ./orbstack-pv/postgres/*
        echo "✅ 本地数据已清理"
    else
        echo "   本地数据目录不存在"
    fi
fi

echo ""
echo "✅ 完全重置完成！"
echo ""
echo "现在可以运行 ./deploy.sh 重新部署"
echo ""
echo "注意:"
echo "   - 所有数据库数据已删除"
echo "   - PVC 和 PV 已重新创建"
echo "   - 应用将从头开始部署"
