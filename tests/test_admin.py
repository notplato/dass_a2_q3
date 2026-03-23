import requests
from api_helpers import get, BASE_URL, ROLL_NUMBER

class TestAdminEndpoints:

    def test_get_all_users(self):
        r = get("/admin/users")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_single_user(self, user_id):
        r = get(f"/admin/users/{user_id}")
        assert r.status_code == 200
        data = r.json()
        assert "wallet_balance" in data and "loyalty_points" in data

    def test_get_all_carts(self):
        r = get("/admin/carts")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_all_orders(self):
        r = get("/admin/orders")
        assert r.status_code == 200
        data = r.json()[0]
        assert isinstance(r.json(), list)
        assert "payment_method" in data and "payment_status" in data and "order_status" in data  

    def test_get_all_products_includes_inactive(self):
        r = get("/admin/products")
        assert r.status_code == 200
        products = r.json()
        assert isinstance(products, list)

    def test_get_all_coupons(self):
        r = get("/admin/coupons")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_all_tickets(self):
        r = get("/admin/tickets")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_all_addresses(self):
        r = get("/admin/addresses")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_admin_does_not_require_user_id(self):
        """Admin endpoints must work without X-User-ID."""
        r = requests.get(f"{BASE_URL}/admin/users",
                         headers={"X-Roll-Number": ROLL_NUMBER})
        assert r.status_code == 200