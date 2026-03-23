from api_helpers import get, put, BASE_URL, ROLL_NUMBER

class TestProfile:

    def test_get_profile(self, user_id):
        r = get("/profile", user_id)
        assert r.status_code == 200

    def test_update_profile_valid(self, user_id):
        r = put("/profile", {"name": "Test User", "phone": "9876543210"}, user_id)
        assert r.status_code == 200

    def test_update_profile_name_too_short(self, user_id):
        """Name < 2 chars must return 400."""
        r = put("/profile", {"name": "A", "phone": "9876543210"}, user_id)
        assert r.status_code == 400

    def test_update_profile_name_too_long(self, user_id):
        """Name > 50 chars must return 400."""
        r = put("/profile", {"name": "A" * 51, "phone": "9876543210"}, user_id)
        assert r.status_code == 400

    def test_update_profile_name_exactly_2_chars(self, user_id):
        """Name of exactly 2 chars is boundary-valid."""
        r = put("/profile", {"name": "AB", "phone": "9876543210"}, user_id)
        assert r.status_code == 200

    def test_update_profile_name_exactly_50_chars(self, user_id):
        """Name of exactly 50 chars is boundary-valid."""
        r = put("/profile", {"name": "A" * 50, "phone": "9876543210"}, user_id)
        assert r.status_code == 200

    def test_update_profile_phone_too_short(self, user_id):
        """Phone with 9 digits must return 400."""
        r = put("/profile", {"name": "Test User", "phone": "987654321"}, user_id)
        assert r.status_code == 400

    def test_update_profile_phone_too_long(self, user_id):
        """Phone with 11 digits must return 400."""
        r = put("/profile", {"name": "Test User", "phone": "98765432101"}, user_id)
        assert r.status_code == 400

    def test_update_profile_phone_with_letters(self, user_id):
        """Phone containing letters must return 400."""
        r = put("/profile", {"name": "Test User", "phone": "98765abcde"}, user_id)
        assert r.status_code == 400

    def test_update_profile_phone_exactly_10_digits(self, user_id):
        """Phone with exactly 10 digits is boundary-valid."""
        r = put("/profile", {"name": "Valid Name", "phone": "1234567890"}, user_id)
        assert r.status_code == 200

    def test_update_profile_missing_phone_returns_400(self, user_id):
        r = put("/profile", {"name": "Valid Name"}, user_id)
        assert r.status_code == 400

    def test_update_profile_name_is_integer_returns_400(self, user_id):
        r = put("/profile", {"name": 12345, "phone": "9876543210"}, user_id)
        assert r.status_code == 400