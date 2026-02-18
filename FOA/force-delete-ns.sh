#!/bin/bash

# 检查输入参数
if [ -z "$1" ]; then
  echo "使用方法: ./force-delete-ns.sh <namespace-name>"
  exit 1
fi

NAMESPACE=$1

echo "--- 正在处理命名空间: $NAMESPACE ---"

# 1. 尝试常规强制删除（后台运行）
kubectl delete ns $NAMESPACE --force --grace-period=0 --timeout=10s &>/dev/null &

# 2. 导出并修改 JSON (移除 finalizers)
echo "Step 1: 正在生成临时配置文件..."
kubectl get namespace $NAMESPACE -o json | \
jq '.spec.finalizers = []' > tmp_ns.json

if [ ! -s tmp_ns.json ]; then
    echo "错误: 无法获取命名空间信息，请检查名称是否正确。"
    exit 1
fi

# 3. 开启代理并提交修改
echo "Step 2: 正在通过 API 强制清除 Finalizers..."
# 在后台启动 proxy，并记录 PID 以后续关闭
kubectl proxy --port=8001 &
PROXY_PID=$!

# 等待代理启动
sleep 2

# 执行 PUT 请求
curl -k -H "Content-Type: application/json" \
     -X PUT \
     --data-binary @tmp_ns.json \
     "http://127.0.0.1:8001/api/v1/namespaces/$NAMESPACE/finalize"

# 4. 清理现场
kill $PROXY_PID
rm tmp_ns.json

echo -e "\n--- 处理完成！请检查: kubectl get ns $NAMESPACE ---"
echo "API 检查kubectl get --raw /api/v1/namespaces/<your-namespace>"
echo "# 检查是否还有任何资源属于该命名空间 kubectl get all,cm,secret,ing -n <your-namespace>"
