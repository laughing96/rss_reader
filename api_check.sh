#!/bin/sh

# # port-forward
# kubectl port-forward svc/redis 6379:6379 -n hackernews >/dev/null 2>/dev/null  &
#
# kubectl port-forward svc/postgres 5432:5432 -n hackernews >/dev/null 2>/dev/null  &

# 测试后端combine接口
curl -v 'http://127.0.0.1:8000/api/combined?limit=50'
