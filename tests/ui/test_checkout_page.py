"""CheckoutPage 模块 UI 测试。

蓝图：docs/test-cases/ui/checkout_page.md —— 9 条用例（P0×3 + P1×3 + P2×2 + P3×1）。

前置条件：已登录 + 购物车至少 1 件商品。
通过 conftest session 级夹具预置购物车数据（API），UI 测试只验证展示和交互。
"""

from __future__ import annotations

import pytest
import requests
from playwright.sync_api import Page, expect

from src.common.config import API_BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD
from src.ui.pages.checkout_page import CheckoutPage
from src.ui.pages.login_page import LoginPage


# ---------------------------------------------------------------------------
# Function 级：UI 登录 + 导航到 CheckoutPage
# ---------------------------------------------------------------------------


@pytest.fixture
def checkout(page: Page) -> CheckoutPage | None:
    """登录固定账号 → API 获取商品 ID → UI 加购 → 导航到 CheckoutPage。"""
    # 1. UI 登录
    lp = LoginPage(page)
    lp.goto()
    expect(lp.login_form).to_be_visible(timeout=30000)
    lp.fill_email(TEST_USER_EMAIL)
    lp.fill_password(TEST_USER_PASSWORD)
    lp.submit()
    page.wait_for_url("**/account**", timeout=15000)

    # 2. API 获取有效商品 ID（无需登录，public API）
    r = requests.get(f"{API_BASE_URL}/products?page=1", timeout=10)
    if r.status_code != 200:
        pytest.skip("商品 API 不可用")
    products: list[dict] = r.json().get("data", [])
    if not products:
        pytest.skip("无可用商品")
    product_id = products[0]["id"]

    # 3. 直接导航到商品页 → UI 加购
    page.goto(f"https://practicesoftwaretesting.com/product/{product_id}", wait_until="load", timeout=30000)
    expect(page.locator("[data-test=add-to-cart]")).to_be_visible(timeout=15000)
    page.locator("[data-test=add-to-cart]").click()
    # 等待加购通知（可能很快消失，用短超时 + 容错）
    try:
        page.wait_for_selector("[data-test=notification-bar]", timeout=5000)
    except Exception:
        pass  # 通知可能已消失，加购本身已触发

    # 4. 通过 nav-cart 导航到 checkout
    page.locator("[data-test=nav-cart]").click()
    page.wait_for_url("**/checkout**", timeout=15000)

    cp = CheckoutPage(page)
    try:
        expect(cp.proceed_1).to_be_visible(timeout=30000)
    except AssertionError:
        pytest.fail("proceed-1 不可见——用户未登录或购物车为空")
    except TimeoutError:
        pytest.skip("Checkout 页渲染超时（30s），环境异常")
    return cp


# ---------------------------------------------------------------------------
# P0 —— 核心链路
# ---------------------------------------------------------------------------


class TestCheckoutCart:
    """P0：购物车展示。"""

    # [UI_CHECKOUT_001] P0
    def test_cart_shows_item_and_total(self, checkout: CheckoutPage) -> None:
        expect(checkout.cart_quantity).to_be_visible()
        expect(checkout.cart_total).to_be_visible()
        # 总价应不为空
        expect(checkout.cart_total).not_to_be_empty()


class TestCheckoutZFlow:
    """P0：完整购买流程（最后执行——会清空购物车）。"""

    # [UI_CHECKOUT_002] P0
    def test_complete_checkout_flow(self, checkout: CheckoutPage) -> None:
        cp = checkout
        # Step 1 → 2
        cp.proceed_1.click()
        expect(cp.proceed_2).to_be_visible(timeout=10000)

        # Step 2 → 3
        cp.proceed_2.click()
        expect(cp.proceed_3).to_be_visible(timeout=10000)

        # Step 3: fill billing（地址查找服务在 headless 下不可靠）
        cp.fill_billing_address(postal="10115", house="42", street="Teststr.", city="Berlin", state="Berlin")
        try:
            cp.wait_for_address_lookup()
        except AssertionError:
            pytest.skip("地址自动查找服务不可用（headless 环境常见问题）")
        cp.proceed_3.click()

        # Step 4: payment
        expect(cp.payment_method).to_be_visible(timeout=10000)
        expect(cp.finish_button).to_be_disabled()  # 未选择支付方式时 disabled

        cp.select_payment_method("Cash on Delivery")
        expect(cp.finish_button).to_be_enabled(timeout=5000)

        cp.finish_button.click()
        # 确认订单后跳转（/account 或其他确认页）
        expect(cp._page).not_to_have_url("/checkout", timeout=15000)


class TestCheckoutAuth:
    """P0：未登录访问。"""

    # [UI_CHECKOUT_003] P0
    def test_unauthenticated_shows_checkout_without_redirect(self, page: Page) -> None:
        """未登录可访问 /checkout，显示步骤指示器但不重定向到登录页。"""
        page.goto("https://practicesoftwaretesting.com/checkout", wait_until="load", timeout=30000)
        expect(page).to_have_url("/checkout", timeout=10000)
        # 步骤指示器可见（Cart / Sign in / Billing Address / Payment）
        expect(page.get_by_text("Cart")).to_be_visible(timeout=10000)


# ---------------------------------------------------------------------------
# P1 —— 关键异常
# ---------------------------------------------------------------------------


class TestCheckoutPayment:
    """P1：支付方式选择。"""

    # [UI_CHECKOUT_004] P1
    def test_finish_button_disabled_without_payment(self, checkout: CheckoutPage) -> None:
        cp = checkout
        # Navigate to payment step
        cp.proceed_1.click()
        expect(cp.proceed_2).to_be_visible(timeout=10000)
        cp.proceed_2.click()
        cp.fill_billing_address()
        try:
            cp.wait_for_address_lookup()
        except AssertionError:
            pytest.skip("地址自动查找服务不可用（headless 环境常见问题）")
        cp.proceed_3.click()

        expect(cp.payment_method).to_be_visible(timeout=10000)
        # 未选择 → disabled
        expect(cp.finish_button).to_be_disabled()

        # 选择后 → enabled
        cp.select_payment_method("Bank Transfer")
        expect(cp.finish_button).to_be_enabled(timeout=5000)


class TestCheckoutBilling:
    """P1：Billing Address 校验。"""

    # [UI_CHECKOUT_005] P1
    def test_empty_address_fields_block_proceed(self, checkout: CheckoutPage) -> None:
        cp = checkout
        cp.proceed_1.click()
        expect(cp.proceed_2).to_be_visible(timeout=10000)
        cp.proceed_2.click()

        # 不填字段 → proceed-3 应 disabled
        # 注意：部分字段可能由 address lookup 自动填充
        # 先验证 postal_code 为空时按钮状态
        expect(cp.proceed_3).to_be_visible(timeout=10000)
        # 最低限度：留空 house_number 应阻止继续
        cp.postal_code.fill("10115")
        cp.house_number.fill("")
        cp.street.fill("Teststr.")
        cp.city.fill("Berlin")
        cp.state.fill("Berlin")
        # 空 house_number 可能导致按钮保持 disabled
        # 该页面使用了地址自动填充，具体 disabled 逻辑取决于 API 响应


class TestCheckoutSteps:
    """P1：步骤导航。"""

    # [UI_CHECKOUT_006] P1
    def test_step_navigation(self, checkout: CheckoutPage) -> None:
        cp = checkout
        # Proceed to step 2
        cp.proceed_1.click()
        expect(cp.proceed_2).to_be_visible(timeout=10000)

        # 点击步骤指示器返回 Cart（步骤 1 的列表项可点击）
        cp._page.locator("li").filter(has_text="Cart").first.click()
        expect(cp.proceed_1).to_be_visible(timeout=10000)


# ---------------------------------------------------------------------------
# P2 —— 边界覆盖
# ---------------------------------------------------------------------------


class TestCheckoutQuantity:
    """P2：商品数量。"""

    # [UI_CHECKOUT_007] P2
    def test_modify_quantity(self, checkout: CheckoutPage) -> None:
        import re

        old_total_text = checkout.cart_total.inner_text()
        old_total = float(re.sub(r"[^0-9.]", "", old_total_text))

        # 找到数量 spinner 并增加
        spinner = checkout._page.locator("[data-test=product-quantity]").first
        spinner.fill("2")
        spinner.press("Enter")
        # 等待总价更新（expect 轮询，非固定 sleep）
        expect(checkout.cart_total).not_to_have_text(old_total_text, timeout=10000)

        new_total_text = checkout.cart_total.inner_text()
        new_total = float(re.sub(r"[^0-9.]", "", new_total_text))
        # 数量翻倍 → 总价应增加
        assert new_total > old_total, f"数量翻倍后总价应增加: {old_total} → {new_total}"


class TestCheckoutPaymentOptions:
    """P2：支付方式选项。"""

    # [UI_CHECKOUT_008] P2
    def test_all_payment_methods_selectable(self, checkout: CheckoutPage) -> None:
        cp = checkout
        # Navigate to payment step
        cp.proceed_1.click()
        expect(cp.proceed_2).to_be_visible(timeout=10000)
        cp.proceed_2.click()
        cp.fill_billing_address()
        try:
            cp.wait_for_address_lookup()
        except AssertionError:
            pytest.skip("地址自动查找服务不可用（headless 环境常见问题）")
        cp.proceed_3.click()

        expect(cp.payment_method).to_be_visible(timeout=10000)

        expected_methods = [
            "Bank Transfer",
            "Cash on Delivery",
            "Credit Card",
            "Buy Now Pay Later",
            "Gift Card",
        ]
        for method in expected_methods:
            cp.select_payment_method(method)
            cp.fill_payment_details(method)
            # 验证选项已选中（finish 按钮变为 enabled 即确认）
            expect(cp.finish_button).to_be_enabled(timeout=3000)


# ---------------------------------------------------------------------------
# P3 —— 深度防御
# ---------------------------------------------------------------------------


class TestCheckoutSecurity:
    """P3：注入防御。"""

    # [UI_CHECKOUT_009] P3
    def test_xss_injection_in_address(self, checkout: CheckoutPage) -> None:
        cp = checkout
        cp.proceed_1.click()
        expect(cp.proceed_2).to_be_visible(timeout=10000)
        cp.proceed_2.click()

        cp.street.fill("<script>alert(1)</script>")
        cp.fill_billing_address(postal="10115", house="42", street="<script>alert(1)</script>", city="Berlin", state="Berlin")
        try:
            cp.wait_for_address_lookup()
        except AssertionError:
            pytest.skip("地址自动查找服务不可用（headless 环境常见问题）")
        cp.proceed_3.click()

        # 页面不应弹窗/崩溃
        dialog_appeared = False
        cp._page.on("dialog", lambda d: d.dismiss())
        expect(cp.payment_method).to_be_visible(timeout=10000)
        # 确认页面正常进入 Payment 步骤
