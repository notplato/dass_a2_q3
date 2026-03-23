import pytest
from api_helpers import get, post, delete

class TestCoupons:

    @pytest.fixture(autouse=True)
    def setup(self, user_id):
        self.uid = user_id
        delete("/cart/clear", user_id)
        yield
        delete("/cart/clear", user_id)
        post("/coupon/remove", {}, user_id)

    def test_apply_invalid_coupon_code(self):
        """Non-existent coupon code must return 4xx."""
        r = post("/coupon/apply", {"code": "INVALIDCODE999"}, self.uid)
        assert r.status_code in (400, 404)

    def test_apply_coupon_expired(self, coupon_code):
        """Expired coupons must be rejected."""
        # This test relies on having an expired coupon in the system
        if coupon_code is None:
            pytest.skip("No coupon available")
        coupons = get("/admin/coupons").json()
        from datetime import datetime
        expired = [c for c in coupons if c.get("expiry_date") and
                   datetime.fromisoformat(c["expiry_date"].replace("Z", "+00:00")).timestamp() <
                   datetime.now().timestamp()]
        if not expired:
            pytest.skip("No expired coupon available")
        r = post("/coupon/apply", {"coupon_code": expired[0]["coupon_code"]}, self.uid)
        assert r.status_code == 400

    def test_apply_coupon_min_cart_not_met(self, product_id, coupon_code):
        """Coupon with min_cart_value not met must return 400."""
        if coupon_code is None:
            pytest.skip("No coupon available")
        # Add only 1 unit of a cheap item
        post("/cart/add", {"product_id": product_id, "quantity": 1}, self.uid)
        coupons = get("/admin/coupons").json()
        high_min = [c for c in coupons if c.get("min_cart_value", 0) > 500]
        if not high_min:
            pytest.skip("No coupon with very high min_cart_value")
        r = post("/coupon/apply", {"coupon_code": high_min[0]["coupon_code"]}, self.uid)
        assert r.status_code == 400

    def test_remove_coupon(self):
        r = post("/coupon/remove", {}, self.uid)
        assert r.status_code in (200, 400)  # 400 if no coupon applied


    def test_apply_coupon_fixed_math(self, product_id):
        """FIXED coupon must exactly deduct the discount_value."""
        coupons = get("/admin/coupons").json()
        fixed_coupons = [c for c in coupons if c.get("discount_type") == "FIXED"]
        if not fixed_coupons:
            pytest.skip("No FIXED coupons available to test")
            
        coupon = fixed_coupons[0]
        # Add enough items to pass min_cart_value
        min_val = coupon.get("min_cart_value", 0)
        post("/cart/add", {"product_id": product_id, "quantity": int(min_val / 10) + 1}, self.uid)
        
        cart_before = get("/cart", self.uid).json()
        total_before = cart_before.get("total", cart_before.get("cart_total", 0))
        
        r = post("/coupon/apply", {"coupon_code": coupon["coupon_code"]}, self.uid)
        assert r.status_code == 200
        
        cart_after = get("/cart", self.uid).json()
        total_after = cart_after.get("total", cart_after.get("cart_total", 0))
        
        expected_total = max(0, total_before - coupon["discount_value"])
        assert abs(total_after - expected_total) < 0.01

    def test_apply_coupon_percent_math_and_cap(self, product_id):
        """PERCENT coupon must deduct exact percentage, respecting max_discount."""
        coupons = get("/admin/coupons").json()
        percent_coupons = [c for c in coupons if c.get("discount_type") == "PERCENT"]
        if not percent_coupons:
            pytest.skip("No PERCENT coupons available to test")
            
        coupon = percent_coupons[0]
        min_val = coupon.get("min_cart_value", 0)
        
        # Buy a massive quantity to ensure we hit the cap if it exists
        post("/cart/add", {"product_id": product_id, "quantity": 100}, self.uid)
        
        cart_before = get("/cart", self.uid).json()
        total_before = cart_before.get("total", cart_before.get("cart_total", 0))
        
        r = post("/coupon/apply", {"code": coupon["code"]}, self.uid)
        assert r.status_code == 200
        
        cart_after = get("/cart", self.uid).json()
        total_after = cart_after.get("total", cart_after.get("cart_total", 0))
        
        calculated_discount = total_before * (coupon["discount_value"] / 100.0)
        max_discount = coupon.get("max_discount")
        
        if max_discount and calculated_discount > max_discount:
            expected_discount = max_discount
        else:
            expected_discount = calculated_discount
            
        expected_total = max(0, total_before - expected_discount)
        assert abs(total_after - expected_total) < 0.01