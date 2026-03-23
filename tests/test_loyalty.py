import pytest
import requests
from api_helpers import get, post, put, delete, BASE_URL, ROLL_NUMBER

class TestLoyalty:

    def test_get_loyalty_points(self, user_id):
        r = get("/loyalty", user_id)
        assert r.status_code == 200
        body = r.json()
        assert "loyalty_points" in body

    def test_redeem_zero_points_returns_400(self, user_id):
        r = post("/loyalty/redeem", {"points": 0}, user_id)
        assert r.status_code == 400

    def test_redeem_negative_points_returns_400(self, user_id):
        r = post("/loyalty/redeem", {"points": -1}, user_id)
        assert r.status_code == 400

    def test_redeem_more_than_available_returns_400(self, user_id):
        body = get("/loyalty", user_id).json()
        pts_key = "loyalty_points"
        current = body[pts_key]
        r = post("/loyalty/redeem", {"points": current + 99999}, user_id)
        assert r.status_code == 400

    def test_redeem_one_point_if_available(self, user_id):
        body = get("/loyalty", user_id).json()
        pts_key = "loyalty_points"
        if body[pts_key] >= 1:
            r = post("/loyalty/redeem", {"points": 1}, user_id)
            assert r.status_code == 200
        else:
            pytest.skip("User has no loyalty points")
