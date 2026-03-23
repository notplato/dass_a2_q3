import pytest
import requests
from api_helpers import BASE_URL, ROLL_NUMBER

@pytest.fixture(scope="session")
def user_id():
    """Fetch a valid user_id from admin endpoint."""
    r = requests.get(f"{BASE_URL}/admin/users", headers={"X-Roll-Number": ROLL_NUMBER})
    assert r.status_code == 200
    users = r.json()
    assert len(users) > 0, "No users in DB – cannot run user-scoped tests"
    return users[0]["user_id"] if isinstance(users[0], dict) and "user_id" in users[0] else users[0]["id"]

@pytest.fixture(scope="session")
def product_id():
    """Fetch a valid active product_id."""
    r = requests.get(f"{BASE_URL}/admin/products", headers={"X-Roll-Number": ROLL_NUMBER})
    assert r.status_code == 200
    products = r.json()
    active = [p for p in products if p.get("is_active", True)]
    assert len(active) > 0, "No active products in DB"
    return active[0]["product_id"] if "product_id" in active[0] else active[0]["id"]

@pytest.fixture(scope="session")
def coupon_code():
    """Fetch a valid coupon code."""
    r = requests.get(f"{BASE_URL}/admin/coupons", headers={"X-Roll-Number": ROLL_NUMBER})
    if r.status_code == 200:
        coupons = r.json()
        if coupons:
            return coupons[0].get("coupon_code", None)
    return None
