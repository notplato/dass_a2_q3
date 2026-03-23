from api_helpers import get, post

class TestWallet:

    def test_get_wallet(self, user_id):
        r = get("/wallet", user_id)
        assert r.status_code == 200
        body = r.json()
        assert "wallet_balance" in body

    def test_add_money_valid(self, user_id):
        r = post("/wallet/add", {"amount": 100}, user_id)
        assert r.status_code == 200

    def test_add_money_amount_zero_returns_400(self, user_id):
        r = post("/wallet/add", {"amount": 0}, user_id)
        assert r.status_code == 400

    def test_add_money_negative_returns_400(self, user_id):
        r = post("/wallet/add", {"amount": -50}, user_id)
        assert r.status_code == 400

    def test_add_money_exactly_100000_is_valid(self, user_id):
        r = post("/wallet/add", {"amount": 100000}, user_id)
        assert r.status_code == 200

    def test_add_money_above_100000_returns_400(self, user_id):
        r = post("/wallet/add", {"amount": 100001}, user_id)
        assert r.status_code == 400

    def test_add_money_updates_balance(self, user_id):
        before = get("/wallet", user_id).json()
        bal_key = "wallet_balance"
        old_bal = before[bal_key]
        post("/wallet/add", {"amount": 500}, user_id)
        after = get("/wallet", user_id).json()
        assert after[bal_key] == old_bal + 500

    def test_wallet_pay_valid(self, user_id):
        post("/wallet/add", {"amount": 200}, user_id)
        r = post("/wallet/pay", {"amount": 100}, user_id)
        assert r.status_code == 200

    def test_wallet_pay_zero_returns_400(self, user_id):
        r = post("/wallet/pay", {"amount": 0}, user_id)
        assert r.status_code == 400

    def test_wallet_pay_negative_returns_400(self, user_id):
        r = post("/wallet/pay", {"amount": -1}, user_id)
        assert r.status_code == 400

    def test_wallet_pay_insufficient_funds_returns_400(self, user_id):
        """Paying more than balance must return 400."""
        bal = get("/wallet", user_id).json()
        bal_key = "wallet_balance"
        current = bal[bal_key]
        r = post("/wallet/pay", {"amount": current + 100000}, user_id)
        assert r.status_code == 400

    def test_wallet_pay_deducts_exact_amount(self, user_id):
        """Exactly the requested amount must be deducted — no extra."""
        post("/wallet/add", {"amount": 500}, user_id)
        before = get("/wallet", user_id).json()
        bal_key = "wallet_balance"
        old = before[bal_key]
        post("/wallet/pay", {"amount": 200}, user_id)
        after = get("/wallet", user_id).json()
        assert after[bal_key] - (old - 200) < 0.000001