"""
pytest_runner MCP Server（FastMCP）

功能：
- run_pytest(target="all")
- run_nodeid(nodeid)
- run_last_failed()

依赖：
    uv add "mcp>=1.28"
"""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# --------------------------------------------------
# 基础配置
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

mcp = FastMCP("pytest-runner")


# --------------------------------------------------
# 工具函数
# --------------------------------------------------

def parse_summary(stdout: str) -> dict:
    """解析 pytest 最终统计。"""

    result = {}

    for key in ("passed", "failed", "skipped", "error", "errors"):
        m = re.search(rf"(\d+)\s+{key}", stdout)
        if m:
            result[key] = int(m.group(1))

    return result


def find_test_file(target: str) -> str:
    """
    cart            -> tests/api/test_cart_api.py
    test_cart_api   -> tests/api/test_cart_api.py
    """

    pattern = (
        f"{target}.py"
        if target.startswith("test_")
        else f"test_{target}_*.py"
    )

    matches = list((PROJECT_ROOT / "tests").rglob(pattern))

    if not matches:
        raise FileNotFoundError(f"找不到测试文件：{target}")

    return str(matches[0].relative_to(PROJECT_ROOT))


def run(args: list[str]) -> dict:
    """执行 pytest。"""

    cmd = [
        "uv", "run", "pytest",
        "-q",
        "--tb=line",
        "--no-header",
    ]

    cmd.extend(args)

    start = time.perf_counter()

    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=600,
    )

    elapsed = round(time.perf_counter() - start, 2)

    return {
        "success": result.returncode == 0,
        "exit_code": result.returncode,
        "duration": elapsed,
        "command": " ".join(cmd),
        **parse_summary(result.stdout),
        "stdout": result.stdout[-3000:],
        "stderr": result.stderr[-1000:],
    }


# --------------------------------------------------
# MCP Tools
# --------------------------------------------------

@mcp.tool()
def run_pytest(target: str = "all") -> dict:
    """
    运行 pytest。

    参数：
        all              -> 全量
        cart             -> cart 模块
        test_cart_api    -> 指定文件
    """

    if target == "all":
        args = ["tests/api/"]
    else:
        args = [find_test_file(target)]

    return run(args)


@mcp.tool()
def run_nodeid(nodeid: str) -> dict:
    """
    运行单个 NodeID。

    示例：

    tests/api/test_user_api.py::TestLogin::test_success
    """

    return run([nodeid])


@mcp.tool()
def run_last_failed() -> dict:
    """重跑最近失败的测试。"""

    return run(["--lf", "tests/api/"])


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":
    mcp.run()
