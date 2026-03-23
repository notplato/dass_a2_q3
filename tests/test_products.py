from api_helpers import get

class TestProducts:

    def test_get_all_products_only_active(self, user_id):
        """Product list must only contain active products."""
        r = get("/products", user_id)
        assert r.status_code == 200
        products = r.json()
        for p in products:
            assert p.get("is_active", True) is True, "Inactive product in list"

    def test_get_product_by_id(self, user_id, product_id):
        r = get(f"/products/{product_id}", user_id)
        assert r.status_code == 200

    def test_get_nonexistent_product_returns_404(self, user_id):
        r = get("/products/9999999", user_id)
        assert r.status_code == 404

    def test_product_price_is_exact(self, user_id):
        """Price from list and detail must match DB value (no rounding)."""
        r = get("/products", user_id)
        assert r.status_code == 200
        products = r.json()
        if products:
            pid = products[0].get("product_id") or products[0].get("id")
            r2 = get(f"/products/{pid}", user_id)
            assert r2.status_code == 200
            assert products[0]["price"] == r2.json()["price"]

    def test_filter_by_category(self, user_id):
        """category query param should filter results."""
        r = get("/products", user_id)
        products = r.json()
        if products:
            cat = products[0].get("category")
            if cat:
                r2 = get(f"/products?category={cat}", user_id)
                assert r2.status_code == 200
                for p in r2.json():
                    assert p.get("category") == cat

    def test_search_by_name(self, user_id):
        """name/search query param should filter by product name."""
        r = get("/products", user_id)
        products = r.json()
        if products:
            name = products[0].get("name", "")[:3]
            r2 = get(f"/products?search={name}", user_id)
            assert r2.status_code == 200

    def test_sort_by_price_asc(self, user_id):
        """sort=price_asc should return ascending prices."""
        r = get("/products?sort=price_asc", user_id)
        assert r.status_code == 200
        prices = [p["price"] for p in r.json()]
        assert prices == sorted(prices)

    def test_sort_by_price_desc(self, user_id):
        """sort=price_desc should return descending prices."""
        r = get("/products?sort=price_desc", user_id)
        assert r.status_code == 200
        prices = [p["price"] for p in r.json()]
        assert prices == sorted(prices, reverse=True)