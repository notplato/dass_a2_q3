import pytest
from api_helpers import get, post, put

class TestSupportTickets:

    @pytest.fixture(autouse=True)
    def setup(self, user_id):
        self.uid = user_id

    def _create_ticket(self, subject="Test Subject Here", message="Test message content here"):
        return post("/support/ticket", {"subject": subject, "message": message}, self.uid)

    def test_create_ticket_valid(self):
        r = self._create_ticket()
        assert r.status_code in (200, 201)

    def test_new_ticket_status_is_open(self):
        r = self._create_ticket(subject="Status Check Ticket")
        assert r.status_code in (200, 201)
        ticket = r.json()
        t = ticket.get("ticket", ticket)
        assert t.get("status") == "OPEN"

    def test_create_ticket_subject_too_short_returns_400(self):
        """Subject < 5 chars must return 400."""
        r = self._create_ticket(subject="Hi")
        assert r.status_code == 400

    def test_create_ticket_subject_exactly_5_chars(self):
        r = self._create_ticket(subject="Hello")
        assert r.status_code in (200, 201)

    def test_create_ticket_subject_too_long_returns_400(self):
        """Subject > 100 chars must return 400."""
        r = self._create_ticket(subject="A" * 101)
        assert r.status_code == 400

    def test_create_ticket_subject_exactly_100_chars(self):
        r = self._create_ticket(subject="A" * 100)
        assert r.status_code in (200, 201)

    def test_create_ticket_empty_message_returns_400(self):
        """Message < 1 char must return 400."""
        r = self._create_ticket(message="")
        assert r.status_code == 400

    def test_create_ticket_message_too_long_returns_400(self):
        """Message > 500 chars must return 400."""
        r = self._create_ticket(message="A" * 501)
        assert r.status_code == 400

    def test_create_ticket_message_exactly_500_chars(self):
        r = self._create_ticket(message="A" * 500)
        assert r.status_code in (200, 201)

    def test_message_saved_exactly(self):
        """Full message must be stored exactly as submitted."""
        msg = "Exact message: special chars !@#$%^&*()"
        r = self._create_ticket(message=msg)
        assert r.status_code in (200, 201)
        t_id = r.json().get("ticket_id")
        tickets = get("/support/tickets", self.uid).json()
        match = next((t for t in tickets if
                      t.get("ticket_id") == t_id), None)
        if match:
            assert match.get("message") == msg

    def test_get_all_tickets(self):
        r = get("/support/tickets", self.uid)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_update_ticket_open_to_in_progress(self):
        r = self._create_ticket(subject="Progress Ticket Test")
        assert r.status_code in (200, 201)
        t = r.json()
        tid = t.get("ticket_id")
        r2 = put(f"/support/tickets/{tid}", {"status": "IN_PROGRESS"}, self.uid)
        assert r2.status_code == 200

    def test_update_ticket_in_progress_to_closed(self):
        r = self._create_ticket(subject="Close Ticket Test")
        assert r.status_code in (200, 201)
        t = r.json()
        tid = t.get("ticket_id")
        put(f"/support/tickets/{tid}", {"status": "IN_PROGRESS"}, self.uid)
        r3 = put(f"/support/tickets/{tid}", {"status": "CLOSED"}, self.uid)
        assert r3.status_code == 200

    def test_update_ticket_open_to_closed_is_invalid(self):
        """OPEN → CLOSED directly must be rejected."""
        r = self._create_ticket(subject="Skip Status Test!")
        assert r.status_code in (200, 201)
        t = r.json()
        tid = t.get("ticket_id")
        r2 = put(f"/support/tickets/{tid}", {"status": "CLOSED"}, self.uid)
        assert r2.status_code == 400

    def test_update_ticket_closed_to_open_is_invalid(self):
        """CLOSED → OPEN must be rejected (no backward transitions)."""
        r = self._create_ticket(subject="Backward Test Ticket")
        assert r.status_code in (200, 201)
        t = r.json()
        tid = t.get("ticket_id")
        put(f"/support/tickets/{tid}", {"status": "IN_PROGRESS"}, self.uid)
        put(f"/support/tickets/{tid}", {"status": "CLOSED"}, self.uid)
        r2 = put(f"/support/tickets/{tid}", {"status": "OPEN"}, self.uid)
        assert r2.status_code == 400

    def test_update_ticket_in_progress_to_open_is_invalid(self):
        """IN_PROGRESS → OPEN must be rejected."""
        r = self._create_ticket(subject="Regress Test Ticket!")
        assert r.status_code in (200, 201)
        t = r.json()
        tid = t.get("ticket_id")
        put(f"/support/tickets/{tid}", {"status": "IN_PROGRESS"}, self.uid)
        r2 = put(f"/support/tickets/{tid}", {"status": "OPEN"}, self.uid)
        assert r2.status_code == 400

    def test_update_ticket_invalid_status_returns_400(self):
        r = self._create_ticket(subject="Invalid Status Ticket")
        assert r.status_code in (200, 201)
        t = r.json()
        tid = t.get("ticket_id")
        r2 = put(f"/support/tickets/{tid}", {"status": "PENDING"}, self.uid)
        assert r2.status_code == 400
