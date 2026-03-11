import os
# import pytest

# 使用这个钩子在 pytest 启动时立即运行


def pytest_configure(config):
    os.environ["RUNNING_TESTS"] = "1"
    print("\n--- conftest RUNNING_TESTS env set to 1 ---")  # 调试用打印
