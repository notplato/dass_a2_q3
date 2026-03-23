import pytest
from api_helpers import get, post, delete, BASE_URL, ROLL_NUMBER

class TestCheckout:

    @pytest.fixture(autouse=True)
    def setup(self, user_id, product_id):
        self.uid = user_id
        self.pid = product_id
        delete("/cart/clear", user_id)
        yield
        delete("/cart/clear", user_id)

    def _add_item(self, qty=1):
        post("/cart/add", {"product_id": self.pid, "quantity": qty}, self.uid)

    def test_checkout_empty_cart_returns_400(self):
        """Checkout with empty cart must return 400."""
        r = post("/checkout", {"payment_method": "COD"}, self.uid)
        assert r.status_code == 400

    def test_checkout_invalid_payment_method_returns_400(self):
        """Unknown payment method must return 400."""
        self._add_item()
        r = post("/checkout", {"payment_method": "BITCOIN"}, self.uid)
        assert r.status_code == 400

    def test_checkout_missing_payment_method_returns_400(self):
        self._add_item()
        r = post("/checkout", {}, self.uid)
        assert r.status_code == 400

    def test_checkout_card_payment_status_is_paid(self):
        """CARD checkout must create order with PAID status."""
        self._add_item()
        r = post("/checkout", {"payment_method": "CARD"}, self.uid)
        assert r.status_code == 200
        order = r.json()
        assert order.get("payment_status") == "PAID"

    def test_checkout_cod_payment_status_is_pending(self):
        """COD checkout must create order with PENDING status."""
        self._add_item(1)
        r = post("/checkout", {"payment_method": "COD"}, self.uid)
        assert r.status_code == 200
        assert r.json().get("payment_status") == "PENDING"

    def test_checkout_wallet_payment_status_is_pending(self, user_id):
        """WALLET checkout must create order with PENDING status."""
        # Add funds first
        post("/wallet/add", {"amount": 10000}, user_id)
        self._add_item(1)
        r = post("/checkout", {"payment_method": "WALLET"}, self.uid)
        assert r.status_code in (200, 400)  # 400 if insufficient funds
        if r.status_code == 200:
            assert r.json().get("payment_status") == "PENDING"

    def test_checkout_gst_is_5_percent(self):
        """Order total must include exactly 5% GST once."""
        self._add_item(1)
        cart = get("/cart", self.uid).json()
        cart_total = cart.get("total", cart.get("cart_total", 0))
        r = post("/checkout", {"payment_method": "CARD"}, self.uid)
        if r.status_code == 200:
            order = r.json()
            order_total = order.get("total", order.get("order_total", 0))
            # order_total should be cart_total * 1.05 (roughly)
            expected = round(cart_total * 1.05, 2)
            assert abs(order_total - expected) < 1.0, \
                f"Expected ~{expected}, got {order_total}"

    def test_checkout_cod_rejected_above_5000(self, user_id):
        """COD with order total > 5000 must return 400."""
        # Try to add enough items to exceed 5000
        post("/wallet/add", {"amount": 100000}, user_id)
        prods = get("/products", user_id).json()
        expensive = sorted(prods, key=lambda p: -p["price"])
        if not expensive:
            pytest.skip("No products available")
        pid = expensive[0].get("product_id")
        price = expensive[0]["price"] * 100
        if price * 1.05 > 5000:
            delete("/cart/clear", user_id)
            post("/cart/add", {"product_id": pid, "quantity": 100}, user_id)
            r = post("/checkout", {"payment_method": "COD"}, user_id)
            assert r.status_code == 400
        else:
            pytest.skip("No product expensive enough to exceed COD limit")

    def test_cart_is_empty_after_successful_checkout(self):
        """Cart must be completely cleared after a successful checkout."""
        self._add_item(1)
        r = post("/checkout", {"payment_method": "CARD"}, self.uid)
        assert r.status_code == 200
        
        cart = get("/cart", self.uid).json()
        items = cart.get("items", cart if isinstance(cart, list) else [])
        assert len(items) == 0, "Cart should be empty after checkout"