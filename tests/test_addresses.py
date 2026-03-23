import pytest
from api_helpers import get, post, put, delete

class TestAddresses:

    @pytest.fixture(autouse=True)
    def setup(self, user_id):
        self.uid = user_id

    def _create_address(self, label="HOME", street="123 Main Street", city="Hyderabad",
                        pincode="500001", is_default=False):
        return post("/addresses", {
            "label": label, "street": street, "city": city,
            "pincode": pincode, "is_default": is_default
        }, self.uid)

    def test_create_address_valid_home(self):
        r = self._create_address(label="HOME")
        assert r.status_code == 201

    def test_create_address_valid_office(self):
        r = self._create_address(label="OFFICE")
        assert r.status_code == 201

    def test_create_address_valid_other(self):
        r = self._create_address(label="OTHER")
        assert r.status_code == 201
        data = r.json().get("address", {})

    def test_create_address_invalid_label(self):
        """Invalid label must return 400."""
        r = self._create_address(label="WORK")
        assert r.status_code == 400

    def test_create_address_street_too_short(self):
        """Street < 5 chars must return 400."""
        r = self._create_address(street="123")
        assert r.status_code == 400

    def test_create_address_street_exactly_5_chars(self):
        r = self._create_address(street="12345")
        assert r.status_code == 201

    def test_create_address_street_exactly_100_chars(self):
        r = self._create_address(street="A" * 100)
        assert r.status_code == 201

    def test_create_address_street_too_long(self):
        """Street > 100 chars must return 400."""
        r = self._create_address(street="A" * 101)
        assert r.status_code == 400

    def test_create_address_city_too_short(self):
        """City < 2 chars must return 400."""
        r = self._create_address(city="H")
        assert r.status_code == 400

    def test_create_address_city_exactly_2_chars(self):
        r = self._create_address(city="HY")
        assert r.status_code == 201

    def test_create_address_city_too_long(self):
        """City > 50 chars must return 400."""
        r = self._create_address(city="A" * 51)
        assert r.status_code == 400

    def test_create_address_pincode_too_short(self):
        """Pincode with 5 digits must return 400."""
        r = self._create_address(pincode="50000")
        assert r.status_code == 400

    def test_create_address_pincode_too_long(self):
        """Pincode with 7 digits must return 400."""
        r = self._create_address(pincode="5000011")
        assert r.status_code == 400

    def test_create_address_pincode_letters(self):
        """Pincode with letters must return 400."""
        r = self._create_address(pincode="5000AB")
        assert r.status_code == 400

    def test_create_address_response_contains_required_fields(self):
        """POST /addresses must return address object with all required fields."""
        r = self._create_address()
        assert r.status_code == 201
        body = r.json()
        addr = body.get("address", body)
        for field in ["address_id", "label", "street", "city", "pincode", "is_default"]:
            assert field in addr, f"Missing field: {field}"

    def test_only_one_default_address(self):
        """Setting a new default must unset all other defaults."""
        self._create_address(is_default=True)
        self._create_address(label="OFFICE", is_default=True)
        r = get("/addresses", self.uid)
        assert r.status_code == 200
        defaults = [a for a in r.json() if a.get("is_default") is True]
        assert len(defaults) <= 1, "More than one default address found"

    def test_get_addresses(self):
        r = get("/addresses", self.uid)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_update_address_street(self):
        c = self._create_address()
        assert c.status_code == 201
        body = c.json()
        addr = body.get("address", body)
        addr_id = addr.get("address_id")
        r = put(f"/addresses/{addr_id}", {"street": "456 New Street Ave"}, self.uid)
        assert r.status_code == 200
        updated = r.json().get("address", r.json())
        assert updated["street"] == "456 New Street Ave"

    def test_delete_address(self):
        c = self._create_address(label="OTHER")
        assert c.status_code == 201
        body = c.json()
        addr = body.get("address", body)
        addr_id = addr.get("address_id") or addr.get("id")
        r = delete(f"/addresses/{addr_id}", self.uid)
        assert r.status_code in (200, 204)

    def test_delete_nonexistent_address_returns_404(self):
        r = delete("/addresses/9999999", self.uid)
        assert r.status_code == 404

    def test_create_address_missing_pincode_returns_400(self, user_id):
        r = post("/addresses", {
            "label": "HOME", 
            "street": "123 Main St", 
            "city": "Hyderabad"
        }, user_id)
        assert r.status_code == 400

    def test_create_address_is_default_is_string_returns_400(self, user_id):
        r = post("/addresses", {
            "label": "HOME", "street": "123 Main St", "city": "Hyderabad",
            "pincode": "500001", "is_default": "true"
        }, user_id)
        assert r.status_code == 400

    def test_update_address_cannot_change_label_city_pincode(self):
        """Updating restricted fields must either return 400 or ignore the changes."""
        c = self._create_address(label="HOME", city="Hyderabad", pincode="500001")
        assert c.status_code == 201
        addr_id = c.json().get("address", c.json()).get("address_id") or c.json().get("address", c.json()).get("id")
        
        r = put(f"/addresses/{addr_id}", {
            "street": "123 Valid St",
            "label": "OFFICE",
            "city": "Mumbai",
            "pincode": "400001"
        }, self.uid)
        
        # if it succeeds, it must not have changed the restricted fields
        if r.status_code == 200:
            updated = r.json().get("address", r.json())
            assert updated["label"] == "HOME", "Label should not have changed"
            assert updated["city"] == "Hyderabad", "City should not have changed"
            assert updated["pincode"] == "500001", "Pincode should not have changed"
        else:
            # alternatively, rejecting the request with 400 is also acceptable behavior
            assert r.status_code == 400