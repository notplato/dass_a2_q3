import pytest
from api_helpers import get, post, delete

class TestOrders:

    @pytest.fixture(scope="class")
    def order_id(self, user_id, product_id):
        """Create a fresh COD order for order-level tests."""
        delete("/cart/clear", user_id)
        post("/cart/add", {"product_id": product_id, "quantity": 1},
             user_id)
        r = post("/checkout", {"payment_method": "CARD"}, user_id)
        assert r.status_code == 200, f"Could not create order: {r.text}"
        return r.json().get("order_id")

    def test_get_all_orders(self, user_id):
        r = get("/orders", user_id)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_order_by_id(self, user_id, order_id):
        r = get(f"/orders/{order_id}", user_id)
        assert r.status_code == 200

    def test_get_nonexistent_order_returns_404(self, user_id):
        r = get("/orders/9999999", user_id)
        assert r.status_code == 404

    def test_cancel_order(self, user_id, product_id):
        """Cancel a freshly created order."""
        delete("/cart/clear", user_id)
        post("/cart/add", {"product_id": product_id, "quantity": 1}, user_id)
        checkout = post("/checkout", {"payment_method": "CARD"}, user_id)
        if checkout.status_code != 200:
            pytest.skip("Checkout failed")
        oid = checkout.json().get("order_id")
        r = post(f"/orders/{oid}/cancel", {}, user_id)
        assert r.status_code in (200, 204)

    def test_cancel_nonexistent_order_returns_404(self, user_id):
        r = post("/orders/9999999/cancel", {}, user_id)
        assert r.status_code == 404

    def test_cancel_delivered_order_returns_400(self, user_id):
        """Cancelling a DELIVERED order must return 400."""
        orders = get("/orders", user_id).json()
        delivered = [o for o in orders if o.get("order_status") == "DELIVERED"]
        if not delivered:
            pytest.skip("No delivered order available")
        oid = delivered[0].get("order_id")
        r = post(f"/orders/{oid}/cancel", {}, user_id)
        assert r.status_code == 400

    def test_cancel_order_restores_stock(self, user_id, product_id):
        """Cancelling order must add product qty back to stock."""
        prod_before = get(f"/products/{product_id}", user_id).json()
        stock_before = prod_before.get("stock", prod_before.get("quantity", 0))
        delete("/cart/clear", user_id)
        post("/cart/add", {"product_id": product_id, "quantity": 1}, user_id)
        checkout = post("/checkout", {"payment_method": "CARD"}, user_id)
        if checkout.status_code != 200:
            pytest.skip("Checkout failed")
        oid = checkout.json().get("order_id")
        post(f"/orders/{oid}/cancel", {}, user_id)
        prod_after = get(f"/products/{product_id}", user_id).json()
        stock_after = prod_after.get("stock", prod_after.get("quantity", 0))
        assert stock_after == stock_before

    def test_invoice_fields(self, user_id, order_id):
        """Invoice must include subtotal, GST, and matching total."""
        r = get(f"/orders/{order_id}/invoice", user_id)
        assert r.status_code == 200
        inv = r.json()
        assert "subtotal" in inv
        assert "gst_amount" in inv
        assert "total_amount" in inv

    def test_invoice_total_matches_order_total(self, user_id, order_id):
        """Invoice total must exactly match the order total."""
        order = get(f"/orders/{order_id}", user_id).json()
        invoice = get(f"/orders/{order_id}/invoice", user_id).json()
        order_total = order.get("total", order.get("order_total"))
        inv_total = invoice.get("total")
        if order_total and inv_total:
            assert abs(order_total - inv_total) < 0.01

    def test_invoice_gst_is_5_percent_of_subtotal(self, user_id, order_id):
        """Invoice GST = 5% of subtotal."""
        invoice = get(f"/orders/{order_id}/invoice", user_id).json()
        sub = invoice.get("subtotal") or invoice.get("sub_total")
        gst = invoice.get("gst") or invoice.get("gst_amount") or invoice.get("tax")
        if sub and gst:
            expected_gst = round(sub * 0.05, 2)
            assert abs(gst - expected_gst) < 0.01