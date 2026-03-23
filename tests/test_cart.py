import pytest
from api_helpers import get, post, delete

class TestCart:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, user_id):
        self.uid = user_id
        # Clear cart before each test
        delete("/cart/clear", user_id)
        yield
        delete("/cart/clear", user_id)

    def _add(self, product_id, quantity):
        return post("/cart/add", {"product_id": product_id, "quantity": quantity}, self.uid)

    def test_get_empty_cart(self):
        r = get("/cart", self.uid)
        data = r.json()
        assert r.status_code == 200 and data.get("items") == []

    def test_add_item_valid(self, product_id):
        r = self._add(product_id, 1)
        assert r.status_code == 200

    def test_add_item_quantity_zero_returns_400(self, product_id):
        r = self._add(product_id, 0)
        assert r.status_code == 400

    def test_add_item_quantity_negative_returns_400(self, product_id):
        r = self._add(product_id, -1)
        assert r.status_code == 400

    def test_add_nonexistent_product_returns_404(self):
        r = self._add(9999999, 1)
        assert r.status_code == 404

    def test_add_exceeds_stock_returns_400(self, product_id):
        """Adding quantity > stock must return 400."""
        r = self._add(product_id, 999999)
        assert r.status_code == 400

    def test_add_same_product_accumulates_quantity(self, product_id):
        """Adding same product twice must sum quantities."""
        self._add(product_id, 1)
        self._add(product_id, 2)
        r = get("/cart", self.uid)
        items = r.json().get("items", r.json())
        item = next((i for i in items if i.get("product_id") == product_id), None)
        assert item is not None
        assert item["quantity"] == 3

    def test_cart_subtotal_is_correct(self, product_id):
        """Item subtotal must equal quantity * unit_price."""
        self._add(product_id, 2)
        r = get("/cart", self.uid)
        items = r.json().get("items", r.json())
        for item in items:
            assert abs(item["subtotal"] - item["quantity"] * item["unit_price"]) < 0.01

    def test_cart_total_is_sum_of_subtotals(self, product_id):
        """Cart total must equal sum of all subtotals."""
        self._add(product_id, 2)
        r = get("/cart", self.uid)
        body = r.json()
        items = body.get("items", [])
        total = body.get("total", body.get("cart_total", None))
        computed = sum(i["subtotal"] for i in items)
        if total is not None:
            assert abs(total - computed) < 0.01

    def test_update_cart_valid_quantity(self, product_id):
        self._add(product_id, 2)
        r = post("/cart/update", {"product_id": product_id, "quantity": 3}, self.uid)
        assert r.status_code == 200

    def test_update_cart_quantity_zero_returns_400(self, product_id):
        self._add(product_id, 2)
        r = post("/cart/update", {"product_id": product_id, "quantity": 0}, self.uid)
        assert r.status_code == 400

    def test_update_cart_quantity_negative_returns_400(self, product_id):
        self._add(product_id, 2)
        r = post("/cart/update", {"product_id": product_id, "quantity": -1}, self.uid)
        assert r.status_code == 400

    def test_remove_item(self, product_id):
        self._add(product_id, 1)
        r = post("/cart/remove", {"product_id": product_id}, self.uid)
        assert r.status_code == 200

    def test_remove_item_not_in_cart_returns_404(self, product_id):
        r = post("/cart/remove", {"product_id": product_id}, self.uid)
        assert r.status_code == 404

    def test_clear_cart(self, product_id):
        self._add(product_id, 1)
        r = delete("/cart/clear", self.uid)
        assert r.status_code in (200, 204)
        r2 = get("/cart", self.uid)
        items = r2.json().get("items", r2.json() if isinstance(r2.json(), list) else [])
        assert len(items) == 0

    def test_add_cart_missing_quantity_returns_400(self, user_id, product_id):
        r = post("/cart/add", {"product_id": product_id}, user_id)
        assert r.status_code == 400

    def test_add_cart_quantity_is_string_returns_400(self, user_id, product_id):
        r = post("/cart/add", {"product_id": product_id, "quantity": "1"}, user_id)
        assert r.status_code == 400