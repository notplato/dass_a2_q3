import requests
from api_helpers import BASE_URL, ROLL_NUMBER

class TestAuthHeaders:

    def test_missing_roll_number_returns_401(self):
        """Missing X-Roll-Number must return 401."""
        r = requests.get(f"{BASE_URL}/admin/users")
        assert r.status_code == 401

    def test_invalid_roll_number_string_returns_400(self):
        """Non-integer X-Roll-Number must return 400."""
        r = requests.get(f"{BASE_URL}/admin/users",
                         headers={"X-Roll-Number": "abc"})
        assert r.status_code == 400

    def test_invalid_roll_number_symbol_returns_400(self):
        """Symbol X-Roll-Number must return 400."""
        r = requests.get(f"{BASE_URL}/admin/users",
                         headers={"X-Roll-Number": "!@#"})
        assert r.status_code == 400

    def test_valid_roll_number_returns_200(self):
        """Valid integer X-Roll-Number must succeed."""
        r = requests.get(f"{BASE_URL}/admin/users",
                         headers={"X-Roll-Number": ROLL_NUMBER})
        assert r.status_code == 200

    def test_missing_user_id_on_user_endpoint_returns_400(self):
        """User-scoped endpoint without X-User-ID must return 400."""
        r = requests.get(f"{BASE_URL}/profile",
                         headers={"X-Roll-Number": ROLL_NUMBER})
        assert r.status_code == 400

    def test_invalid_user_id_zero_returns_400(self, user_id):
        """X-User-ID = 0 is not a positive integer and must return 400."""
        r = requests.get(f"{BASE_URL}/profile",
                         headers={"X-Roll-Number": ROLL_NUMBER, "X-User-ID": "0"})
        assert r.status_code == 400

    def test_invalid_user_id_nonexistent_returns_400(self):
        """X-User-ID that does not exist must return 400."""
        r = requests.get(f"{BASE_URL}/profile",
                         headers={"X-Roll-Number": ROLL_NUMBER, "X-User-ID": "9999999"})
        assert r.status_code == 400

    def test_invalid_user_id_string_returns_400(self):
        """Non-integer X-User-ID must return 400."""
        r = requests.get(f"{BASE_URL}/profile",
                         headers={"X-Roll-Number": ROLL_NUMBER, "X-User-ID": "abc"})
        assert r.status_code == 400

    def test_negative_user_id_returns_400(self):
        """Negative X-User-ID must return 400."""
        r = requests.get(f"{BASE_URL}/profile",
                         headers={"X-Roll-Number": ROLL_NUMBER, "X-User-ID": "-1"})
        assert r.status_code == 400
