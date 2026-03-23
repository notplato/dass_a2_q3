from api_helpers import get, post

class TestReviews:

    def test_get_product_reviews(self, user_id, product_id):
        r = get(f"/products/{product_id}/reviews", user_id)
        assert r.status_code == 200
        assert isinstance(r.json().get("reviews"), list)

    def test_add_review_valid(self, user_id, product_id):
        r = post(f"/products/{product_id}/reviews",
                 {"rating": 4, "comment": "Great product!"}, user_id)
        assert r.status_code in (200, 201)

    def test_add_review_rating_1_is_valid(self, user_id, product_id):
        r = post(f"/products/{product_id}/reviews",
                 {"rating": 1, "comment": "Barely okay."}, user_id)
        assert r.status_code in (200, 201)

    def test_add_review_rating_5_is_valid(self, user_id, product_id):
        r = post(f"/products/{product_id}/reviews",
                 {"rating": 5, "comment": "Excellent!"}, user_id)
        assert r.status_code in (200, 201)

    def test_add_review_rating_0_returns_400(self, user_id, product_id):
        r = post(f"/products/{product_id}/reviews",
                 {"rating": 0, "comment": "Bad"}, user_id)
        assert r.status_code == 400

    def test_add_review_rating_6_returns_400(self, user_id, product_id):
        r = post(f"/products/{product_id}/reviews",
                 {"rating": 6, "comment": "Amazing!!"}, user_id)
        assert r.status_code == 400

    def test_add_review_negative_rating_returns_400(self, user_id, product_id):
        r = post(f"/products/{product_id}/reviews",
                 {"rating": -1, "comment": "Nope"}, user_id)
        assert r.status_code == 400

    def test_add_review_empty_comment_returns_400(self, user_id, product_id):
        r = post(f"/products/{product_id}/reviews",
                 {"rating": 3, "comment": ""}, user_id)
        assert r.status_code == 400

    def test_add_review_comment_too_long_returns_400(self, user_id, product_id):
        r = post(f"/products/{product_id}/reviews",
                 {"rating": 3, "comment": "A" * 201}, user_id)
        assert r.status_code == 400

    def test_add_review_comment_exactly_200_chars(self, user_id, product_id):
        r = post(f"/products/{product_id}/reviews",
                 {"rating": 3, "comment": "A" * 200}, user_id)
        assert r.status_code in (200, 201)

    def test_average_rating_is_decimal_not_floored(self, user_id, product_id):
        """Average rating must be a float, not an integer-floored value."""
        post(f"/products/{product_id}/reviews", {"rating": 3, "comment": "OK"}, user_id)
        post(f"/products/{product_id}/reviews", {"rating": 4, "comment": "Good"}, user_id)
        r = get(f"/products/{product_id}/reviews", user_id)
        reviews = r.json().get("reviews")
        if len(reviews) >= 2:
            ratings = [rev["rating"] for rev in reviews]
            avg = sum(ratings) / len(ratings)
            avg_reported = get(f"/products/{product_id}/reviews", user_id).json().get("average_rating")
            if avg_reported is not None:
                assert abs(avg_reported - avg) < 0.1

    def test_no_reviews_average_rating_is_zero(self, user_id):
        """Product with no reviews must have average_rating = 0."""
        products = get("/admin/products").json()
        # Find product with no reviews
        for p in products:
            pid = p.get("product_id") or p.get("id")
            revs = get(f"/products/{pid}/reviews", user_id)
            if revs.status_code == 200 and len(revs.json()) == 0:
                avg = p.get("average_rating") or \
                      get(f"/products/{pid}", user_id).json().get("average_rating", 0)
                assert avg == 0
                break

    def test_add_review_missing_comment_returns_400(self, user_id, product_id):
        r = post(f"/products/{product_id}/reviews", {"rating": 4}, user_id)
        assert r.status_code == 400

    def test_add_review_decimal_rating_returns_400(self, user_id, product_id):
        """Ratings should be strictly integers 1-5."""
        r = post(f"/products/{product_id}/reviews", {
            "rating": 4.5, "comment": "Pretty good"
        }, user_id)
        assert r.status_code == 400
