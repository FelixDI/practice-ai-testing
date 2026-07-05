"""检测靶场网站是否对 Playwright Chromium 可达。

curl 与 headless Chromium 的请求特征完全不同 —— Cloudflare 对 curl 宽松、
对 Playwright 严格。本脚本用 Playwright 实际导航，消除 curl 检测的假阴性。

用法：uv run python scripts/check_site_reachability.py
输出：最后一行 "blocked=true" 或 "blocked=false"，可被 GitHub Actions 解析。
"""

from __future__ import annotations

import os
import sys

from playwright.sync_api import sync_playwright


def main() -> int:
    blocked = False
    reason = ""

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            resp = page.goto(
                "https://practicesoftwaretesting.com/", timeout=15000
            )
            body = page.content().lower()
            status = resp.status if resp else 0

            if status == 403 and (
                "cloudflare" in body or "checking your browser" in body
            ):
                blocked = True
                reason = f"Cloudflare 拦截 (status={status})"
            elif status != 200:
                blocked = True
                reason = f"站点不可达 (status={status})"
            elif 'data-test="nav-home"' not in body:
                blocked = True
                reason = f"页面未正常渲染 (status={status}, 缺少 nav-home)"
            else:
                reason = f"站点可达，页面正常渲染 (status={status})"
        except Exception as e:
            blocked = True
            reason = f"Playwright 异常: {type(e).__name__}: {e}"
        finally:
            browser.close()

    # GitHub Actions: 写入 GITHUB_OUTPUT 供后续 step 判断
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"blocked={'true' if blocked else 'false'}\n")

    print(reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
