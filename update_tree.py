#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time        : 2026-05-13 14:16
# @Author      : Felix Cui
# @Email       : cuihediyzu@gmail.com
# @File        : update_tree.py
# @PythonEnv   : Python 3.12 (pythonautotest-py312)
# @IDE         : PyCharm
# @Description : local auto update project structure in README.md by git hooks

# 实际项目中可以结合两者：
# GitHub Actions：云工作流团队项目，负责线上定时更新、push 后自动运行的主流程
# 本地 pre-commit hook（可选）：在提交前做快速验证（如拼写检查、数据格式校验），减少 Actions 运行失败的概率


#!/usr/bin/env python3
"""
安全更新 README.md 中的项目目录树。
只替换 <!-- PROJECT_STRUCTURE_START --> 和 <!-- PROJECT_STRUCTURE_END --> 之间的内容。
根目录强制显示为“项目名/”，所有子目录带斜杠。
"""
import subprocess
import sys
from pathlib import Path

README = Path("README.md")
START_MARKER = "<!-- PROJECT_STRUCTURE_START -->"
END_MARKER = "<!-- PROJECT_STRUCTURE_END -->"

def generate_tree() -> str:
    """生成目录树，并将第一行强制替换为 '项目名/'"""
    project_root = Path.cwd()
    project_name = project_root.name
    if not project_name:
        project_name = "Project"  # 兜底

    try:
        result = subprocess.run(
            [
                "tree",
                "-I", "__pycache__|*.pyc|.git|.idea|.DS_Store|venv|env|.venv|mysql_data|jenkins_home|allure-results|allure-report",   # 排除
                "--dirsfirst",
                "-F"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        tree_output = result.stdout.rstrip("\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ tree 命令执行失败: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ 未找到 tree 命令，请先安装: brew install tree")
        sys.exit(1)

    # 分割行
    lines = tree_output.splitlines()
    if not lines:
        # 空输出，返回一个默认树
        return f"{project_name}/"

    # 无论第一行原来是什么（. 或 ./ 或 ./\n），都替换为项目名/
    original_first = lines[0]
    lines[0] = f"{project_name}/"

    # 可选：打印调试信息（确认替换发生）
    # print(f"第一行原为: {repr(original_first)}，已替换为: {lines[0]}")

    return "\n".join(lines)

def update_readme(tree_content: str) -> None:
    """用新的树内容替换 README 中标记区域的内容"""
    if not README.exists():
        print("❌ README.md 不存在")
        sys.exit(1)

    content = README.read_text(encoding="utf-8")
    start_idx = content.find(START_MARKER)
    end_idx = content.find(END_MARKER)

    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        print(f"❌ README.md 中未找到正确的标记 {START_MARKER} 和 {END_MARKER}")
        print("请先在 README.md 中添加这两个标记，并确保开始标记在前，结束标记在后。")
        sys.exit(1)

    before = content[:start_idx + len(START_MARKER)]
    after = content[end_idx:]

    new_block = f"\n```\n{tree_content}\n```\n"
    new_content = before + new_block + after

    README.write_text(new_content, encoding="utf-8")
    print("✅ README.md 项目目录树已更新")

if __name__ == "__main__":
    tree_str = generate_tree()
    update_readme(tree_str)