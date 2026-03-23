# QuickCart API
**Roll Number:** 2024101146  
**Total Test Cases:** 151  
**Passed:** 121 | **Failed:** 30

---

## 1. Authentication & Authorization (`test_auth.py`)

### TC-AUTH-01 — Missing X-Roll-Number
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/admin/users` — no headers |
| **Expected Output** | `401 Unauthorized` |
| **Actual Output** | `401 Unauthorized` |
| **Justification** | The spec mandates every request carry a valid `X-Roll-Number`. Missing it is the primary auth gate and must be hard-blocked. |

### TC-AUTH-02 — Invalid X-Roll-Number (string)
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/admin/users`, `X-Roll-Number: abc` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | The header must be a valid integer. A string is a data-type violation. |

### TC-AUTH-03 — Invalid X-Roll-Number (symbols)
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/admin/users`, `X-Roll-Number: !@#` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Symbol characters are not valid integers; verifies the parser is strict. |

### TC-AUTH-04 — Valid X-Roll-Number
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/admin/users`, `X-Roll-Number: 2024101146` |
| **Expected Output** | `200 OK` |
| **Actual Output** | `200 OK` |
| **Justification** | Baseline positive test confirming valid auth passes. |

### TC-AUTH-05 — Missing X-User-ID on user-scoped endpoint
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/profile`, `X-Roll-Number: 2024101146`, no `X-User-ID` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | User-scoped endpoints require `X-User-ID`; omission must be rejected. |

### TC-AUTH-06 — X-User-ID = 0
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/profile`, `X-User-ID: 0` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | The spec requires a *positive* integer; 0 is not positive. |

### TC-AUTH-07 — Non-existent X-User-ID
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/profile`, `X-User-ID: 9999999` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `404 Not Found` **BUG** |
| **Justification** | The spec says an invalid or non-matching `X-User-ID` must return 400. The server instead returns 404, violating the spec. |

### TC-AUTH-08 — X-User-ID as string
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/profile`, `X-User-ID: abc` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Non-integer `X-User-ID` must be rejected as a malformed request. |

### TC-AUTH-09 — Negative X-User-ID
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/profile`, `X-User-ID: -1` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Negative values are not positive integers and must be rejected. |

---

## 2. Admin Endpoints (`test_admin.py`)

### TC-ADMIN-01 through TC-ADMIN-08 — All Admin List Endpoints
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/admin/{users,carts,orders,products,coupons,tickets,addresses}` with valid roll number, no `X-User-ID` |
| **Expected Output** | `200 OK`, JSON array |
| **Actual Output** | `200 OK` (all 8) |
| **Justification** | Admin endpoints must bypass user-scoping and return full DB state for test verification. Confirming all 8 pass ensures the data inspection layer is fully functional. |

### TC-ADMIN-09 — Admin endpoint does not require X-User-ID
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/admin/users`, roll number only |
| **Expected Output** | `200 OK` |
| **Actual Output** | `200 OK` |
| **Justification** | The spec explicitly states admin endpoints do not require `X-User-ID`. This confirms that user-scoping rules are not accidentally applied to admin routes. |

---

## 3. Profile (`test_profile.py`)

### TC-PROF-01 — Get profile
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/profile`, valid user |
| **Expected Output** | `200 OK` |
| **Actual Output** | `200 OK` |
| **Justification** | Baseline test confirming profile retrieval works. |

### TC-PROF-02 — Valid profile update
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/profile`, `{"name": "Test User", "phone": "9876543210"}` |
| **Expected Output** | `200 OK` |
| **Actual Output** | `200 OK` |
| **Justification** | Happy-path validation ensuring a well-formed request succeeds. |

### TC-PROF-03 — Name too short (1 char)
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/profile`, `{"name": "A", "phone": "9876543210"}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | BVA: just below the minimum of 2 characters. |

### TC-PROF-04 — Name too long (51 chars)
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/profile`, `{"name": "A"*51, "phone": "9876543210"}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | BVA: just above the maximum of 50 characters. |

### TC-PROF-05 — Name exactly 2 chars (lower boundary)
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/profile`, `{"name": "AB", "phone": "9876543210"}` |
| **Expected Output** | `200 OK` |
| **Actual Output** | `200 OK` |
| **Justification** | BVA: exactly at the lower valid boundary — must be accepted. |

### TC-PROF-06 — Name exactly 50 chars (upper boundary)
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/profile`, `{"name": "A"*50, "phone": "9876543210"}` |
| **Expected Output** | `200 OK` |
| **Actual Output** | `200 OK` |
| **Justification** | BVA: exactly at the upper valid boundary — must be accepted. |

### TC-PROF-07 — Phone too short (9 digits)
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/profile`, `{"name": "Test", "phone": "987654321"}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | BVA: one digit below the required 10. |

### TC-PROF-08 — Phone too long (11 digits)
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/profile`, `{"name": "Test", "phone": "98765432101"}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | BVA: one digit above the required 10. |

### TC-PROF-09 — Phone with letters
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/profile`, `{"name": "Test", "phone": "98765abcde"}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | The spec mandates phone must be exactly 10 *digits*. Accepting letters is a validation failure. |

### TC-PROF-10 — Phone exactly 10 digits
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/profile`, `{"name": "Valid", "phone": "1234567890"}` |
| **Expected Output** | `200 OK` |
| **Actual Output** | `200 OK` |
| **Justification** | BVA: exactly at the required 10-digit boundary. |

### TC-PROF-11 — Missing phone field
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/profile`, `{"name": "Valid Name"}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Missing required field must be rejected. |

### TC-PROF-12 — Name as integer (wrong type)
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/profile`, `{"name": 12345, "phone": "9876543210"}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Data-type validation: name must be a string, not a number. |

---

## 4. Addresses (`test_addresses.py`)

> **Note:** All address tests that create a valid address are failing because the server is rejecting a correct 6-digit pincode (`500001`) with a `400` error. This is a server-side validation bug. The test cases themselves are correctly written. See Bug Report (BUG-ADDR-01) for full details.

### TC-ADDR-01 — Create address with label HOME
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"label":"HOME","street":"123 Main Street","city":"Hyderabad","pincode":"500001","is_default":false}` |
| **Expected Output** | `201 Created` |
| **Actual Output** | `400 Bad Request` **BUG (server rejects valid pincode)** |
| **Justification** | Equivalence partitioning — HOME is one of three valid enum values and must be accepted. |

### TC-ADDR-02 — Create address with label OFFICE
| Field | Detail |
|---|---|
| **Input** | Same as above with `"label":"OFFICE"` |
| **Expected Output** | `201 Created` |
| **Actual Output** | `400 Bad Request` **BUG (server rejects valid pincode)** |
| **Justification** | All three valid label values must be tested separately (equivalence partitioning). |

### TC-ADDR-03 — Create address with label OTHER
| Field | Detail |
|---|---|
| **Input** | Same as above with `"label":"OTHER"` |
| **Expected Output** | `201 Created` |
| **Actual Output** | `400 Bad Request` **BUG (server rejects valid pincode)** |
| **Justification** | Same as TC-ADDR-02. |

### TC-ADDR-04 — Invalid label
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"label":"WORK", ...}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | "WORK" is not in the allowed set {HOME, OFFICE, OTHER}; must be rejected. |

### TC-ADDR-05 — Street too short (3 chars)
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"street":"123", ...}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | BVA: below minimum street length of 5. |

### TC-ADDR-06 — Street exactly 5 chars (lower boundary)
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"street":"12345", ...}` |
| **Expected Output** | `201 Created` |
| **Actual Output** | `400 Bad Request` **BUG (server rejects valid pincode)** |
| **Justification** | BVA lower boundary — must be accepted. |

### TC-ADDR-07 — Street exactly 100 chars (upper boundary)
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"street":"A"*100, ...}` |
| **Expected Output** | `201 Created` |
| **Actual Output** | `400 Bad Request` **BUG (server rejects valid pincode)** |
| **Justification** | BVA upper boundary — must be accepted. |

### TC-ADDR-08 — Street too long (101 chars)
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"street":"A"*101, ...}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | BVA: one char above the maximum. |

### TC-ADDR-09 — City too short (1 char)
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"city":"H", ...}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | BVA: below minimum city length of 2. |

### TC-ADDR-10 — City exactly 2 chars (lower boundary)
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"city":"HY", ...}` |
| **Expected Output** | `201 Created` |
| **Actual Output** | `400 Bad Request` **BUG (server rejects valid pincode)** |
| **Justification** | BVA lower boundary — must be accepted. |

### TC-ADDR-11 — City too long (51 chars)
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"city":"A"*51, ...}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | BVA: one char above the maximum. |

### TC-ADDR-12 — Pincode too short (5 digits)
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"pincode":"50000", ...}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | BVA: pincode must be exactly 6 digits. 5 digits should be rejected. |

### TC-ADDR-13 — Pincode too long (7 digits)
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"pincode":"5000011", ...}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | BVA: 7 digits exceeds the exact 6-digit requirement. |

### TC-ADDR-14 — Pincode with letters
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"pincode":"5000AB", ...}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Pincode must be numeric digits only. |

### TC-ADDR-15 — Response contains all required fields
| Field | Detail |
|---|---|
| **Input** | Valid `POST /api/v1/addresses` |
| **Expected Output** | `201 Created`, response body includes `address_id`, `label`, `street`, `city`, `pincode`, `is_default` |
| **Actual Output** | `400 Bad Request` **BUG (server rejects valid pincode)** |
| **Justification** | The spec explicitly lists the required fields the POST response must include. |

### TC-ADDR-16 — Only one default address at a time
| Field | Detail |
|---|---|
| **Input** | Create two addresses both with `is_default: true` |
| **Expected Output** | Only one address has `is_default: true` in `GET /addresses` |
| **Actual Output** |  PASSED` |
| **Justification** | Critical business logic: mutual exclusivity of default addresses. |

### TC-ADDR-17 — Get addresses list
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/addresses` |
| **Expected Output** | `200 OK`, JSON array |
| **Actual Output** | `200 OK` |
| **Justification** | Baseline read test. |

### TC-ADDR-18 — Update address street
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/addresses/{id}`, `{"street":"456 New Street Ave"}` |
| **Expected Output** | `200 OK`, response shows updated street |
| **Actual Output** | `400 Bad Request` **BUG (server rejects valid pincode on create step)** |
| **Justification** | Update must persist and return new street value, not stale old data. |

### TC-ADDR-19 — Delete address
| Field | Detail |
|---|---|
| **Input** | `DELETE /api/v1/addresses/{id}` |
| **Expected Output** | `200` or `204` |
| **Actual Output** | `400 Bad Request` **BUG (create step fails)** |
| **Justification** | Validates the delete lifecycle for an address. |

### TC-ADDR-20 — Delete non-existent address
| Field | Detail |
|---|---|
| **Input** | `DELETE /api/v1/addresses/9999999` |
| **Expected Output** | `404 Not Found` |
| **Actual Output** | `404 Not Found` |
| **Justification** | Deleting a resource that doesn't exist must return 404 per REST conventions. |

### TC-ADDR-21 — Missing required field (no pincode)
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, payload missing `pincode` field |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | All required fields must be present; missing `pincode` must be rejected. |

### TC-ADDR-22 — is_default as string instead of boolean
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/addresses`, `{"is_default": "true"}` (string, not bool) |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Type validation: `is_default` must be a boolean, not a string. |

### TC-ADDR-23 — Update cannot change label, city, or pincode
| Field | Detail |
|---|---|
| **Input** | `PUT /api/v1/addresses/{id}`, payload includes `label`, `city`, `pincode` changes |
| **Expected Output** | Either `400`, or `200` with those fields unchanged |
| **Actual Output** | `400 Bad Request` **BUG (create step fails)** |
| **Justification** | The spec explicitly states only `street` and `is_default` may be updated. Immutable fields must be ignored or rejected. |

---

## 5. Products (`test_products.py`)

### TC-PROD-01 — Active products only in list
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/products` |
| **Expected Output** | `200 OK`, all items have `is_active: true` |
| **Actual Output** | `200 OK` |
| **Justification** | The storefront must never expose inactive products to users. |

### TC-PROD-02 — Get product by ID
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/products/{valid_id}` |
| **Expected Output** | `200 OK` |
| **Actual Output** | `200 OK` |
| **Justification** | Baseline positive retrieval test. |

### TC-PROD-03 — Non-existent product returns 404
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/products/9999999` |
| **Expected Output** | `404 Not Found` |
| **Actual Output** | `404 Not Found` |
| **Justification** | Missing resource must return 404 per REST conventions. |

### TC-PROD-04 — Price exactness (list vs detail)
| Field | Detail |
|---|---|
| **Input** | Compare price in `GET /products` vs `GET /products/{id}` |
| **Expected Output** | Prices match exactly |
| **Actual Output** | Prices match |
| **Justification** | Any floating-point rounding or formatting difference would cause financial errors at checkout. |

### TC-PROD-05 — Filter by category
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/products?category={cat}` |
| **Expected Output** | All returned products have matching category |
| **Actual Output** | |
| **Justification** | Validates category filter returns only matching results. |

### TC-PROD-06 — Search by name
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/products?search={partial_name}` |
| **Expected Output** | `200 OK` |
| **Actual Output** | |
| **Justification** | Search functionality must return relevant results. |

### TC-PROD-07 — Sort price ascending
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/products?sort=price_asc` |
| **Expected Output** | Prices in non-decreasing order |
| **Actual Output** | |
| **Justification** | Confirms sort algorithm correctness. |

### TC-PROD-08 — Sort price descending
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/products?sort=price_desc` |
| **Expected Output** | Prices in non-increasing order |
| **Actual Output** | |
| **Justification** | Confirms reverse sort algorithm correctness. |

---

## 6. Cart (`test_cart.py`)

### TC-CART-01 — Get empty cart
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/cart` after clearing |
| **Expected Output** | `200 OK`, `items: []` |
| **Actual Output** | `200 OK` |
| **Justification** | Baseline empty-state check. |

### TC-CART-02 — Add item valid
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/add`, `{"product_id": 1, "quantity": 1}` |
| **Expected Output** | `200 OK` |
| **Actual Output** | `200 OK` |
| **Justification** | Happy-path item addition. |

### TC-CART-03 — Quantity = 0 returns 400
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/add`, `{"product_id": 1, "quantity": 0}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | The spec states quantity must be at least 1. Quantity 0 must be rejected. |

### TC-CART-04 — Quantity negative returns 400
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/add`, `{"product_id": 1, "quantity": -1}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Negative quantities are nonsensical and must be rejected. |

### TC-CART-05 — Non-existent product returns 404
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/add`, `{"product_id": 9999999, "quantity": 1}` |
| **Expected Output** | `404 Not Found` |
| **Actual Output** | `404 Not Found` |
| **Justification** | Cannot add a product that doesn't exist to cart. |

### TC-CART-06 — Quantity exceeds stock
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/add`, `{"product_id": 1, "quantity": 999999}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Prevents overselling — stock limits must be enforced at cart add time. |

### TC-CART-07 — Same product added twice accumulates quantity
| Field | Detail |
|---|---|
| **Input** | Add product 1 twice (qty 1 then qty 2) |
| **Expected Output** | Cart shows product 1 with qty 3 |
| **Actual Output** | Qty = 3 |
| **Justification** | The spec explicitly requires accumulation, not replacement. |

### TC-CART-08 — Subtotal = quantity × unit_price
| Field | Detail |
|---|---|
| **Input** | Add product (qty 2), fetch cart |
| **Expected Output** | `subtotal == quantity * unit_price` |
| **Actual Output** | `assert 256 < 0.01` **BUG** — subtotal shows `-16` instead of `240` |
| **Justification** | Per-item subtotal math is foundational to correct billing. A negative subtotal indicates a severe arithmetic bug in the server. |

### TC-CART-09 — Cart total = sum of all subtotals
| Field | Detail |
|---|---|
| **Input** | Fetch cart with items |
| **Expected Output** | `total == sum(subtotals)` |
| **Actual Output** | `assert 16 < 0.01` **BUG** — total is `0` while computed sum is `-16` |
| **Justification** | The cart total is the financial basis for checkout. Both values being wrong confirms the subtotal bug cascades into the total. |

### TC-CART-10 — Update cart quantity (valid)
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/update`, `{"product_id": 1, "quantity": 3}` |
| **Expected Output** | `200 OK` |
| **Actual Output** | `200 OK` |
| **Justification** | Valid update must succeed. |

### TC-CART-11 — Update cart quantity to 0
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/update`, `{"product_id": 1, "quantity": 0}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Update quantity must also be at least 1. |

### TC-CART-12 — Update cart quantity negative
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/update`, `{"product_id": 1, "quantity": -1}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Negative update is invalid. |

### TC-CART-13 — Remove item from cart
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/remove`, `{"product_id": 1}` |
| **Expected Output** | `200 OK` |
| **Actual Output** | `200 OK` |
| **Justification** | Standard remove operation. |

### TC-CART-14 — Remove item not in cart returns 404
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/remove`, `{"product_id": 1}` on empty cart |
| **Expected Output** | `404 Not Found` |
| **Actual Output** | `404 Not Found` |
| **Justification** | Removing a non-existent cart item must return 404. |

### TC-CART-15 — Clear cart
| Field | Detail |
|---|---|
| **Input** | `DELETE /api/v1/cart/clear` |
| **Expected Output** | `200`/`204`, cart is empty |
| **Actual Output** | |
| **Justification** | Cart must be fully wiped after clear. |

### TC-CART-16 — Missing quantity field
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/add`, `{"product_id": 1}` (no quantity) |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | `quantity` is a required field; its absence must be rejected. |

### TC-CART-17 — Quantity as string
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/cart/add`, `{"product_id": 1, "quantity": "1"}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Type validation: quantity must be an integer, not a string. |

---

## 7. Coupons (`test_cupons.py`)

### TC-COUP-01 — Invalid coupon code
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/coupon/apply`, `{"code": "INVALIDCODE999"}` |
| **Expected Output** | `400` or `404` |
| **Actual Output** | `400` |
| **Justification** | Non-existent coupon codes must be rejected. |

### TC-COUP-02 — Expired coupon
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/coupon/apply` with an expired coupon code |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Expired promotions must not be applied regardless of other validity. |

### TC-COUP-03 — Minimum cart value not met
| Field | Detail |
|---|---|
| **Input** | Apply coupon with `min_cart_value > 500` to a low-value cart |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Cart-value gating for promotions must be enforced. |

### TC-COUP-04 — Remove coupon
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/coupon/remove` |
| **Expected Output** | `200` or `400` if none applied |
| **Actual Output** | |
| **Justification** | Coupon removal must function correctly. |

### TC-COUP-05 — FIXED coupon discount math
| Field | Detail |
|---|---|
| **Input** | Apply FIXED coupon; compare cart total before and after |
| **Expected Output** | `total_after == total_before - discount_value` |
| **Actual Output** | `400 Bad Request` **BUG** — coupon apply fails even with sufficient cart value |
| **Justification** | Financial accuracy of flat discounts is critical to prevent revenue loss. |

### TC-COUP-06 — PERCENT coupon math with cap
| Field | Detail |
|---|---|
| **Input** | Apply PERCENT coupon to large cart; verify `max_discount` cap is respected |
| **Expected Output** | Discount ≤ `max_discount`, total reduced by exact percentage |
| **Actual Output** | `KeyError: 'code'` **BUG** — the coupon object uses `coupon_code` key, not `code` |
| **Justification** | Percentage discounts with caps must not over-apply, preventing financial losses. |

---

## 8. Checkout (`test_checkout.py`)

### TC-CHKOUT-01 — Empty cart checkout
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/checkout`, `{"payment_method": "COD"}` with empty cart |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | Creating orders from an empty cart must be blocked; otherwise ghost orders are created. |

### TC-CHKOUT-02 — Invalid payment method
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/checkout`, `{"payment_method": "BITCOIN"}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Only COD, WALLET, CARD are valid payment methods. |

### TC-CHKOUT-03 — Missing payment method
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/checkout`, `{}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `400 Bad Request` |
| **Justification** | Required field missing must be rejected. |

### TC-CHKOUT-04 — CARD order status is PAID
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/checkout`, `{"payment_method": "CARD"}` |
| **Expected Output** | `200 OK`, `payment_status: "PAID"` |
| **Actual Output** | `200 OK`, `payment_status: "PAID"` |
| **Justification** | Card payments are instant; order must start as PAID. |

### TC-CHKOUT-05 — COD order status is PENDING
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/checkout`, `{"payment_method": "COD"}` |
| **Expected Output** | `200 OK`, `payment_status: "PENDING"` |
| **Actual Output** | |
| **Justification** | Cash-on-delivery is deferred payment; order must start as PENDING. |

### TC-CHKOUT-06 — WALLET order status is PENDING
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/checkout`, `{"payment_method": "WALLET"}` |
| **Expected Output** | `payment_status: "PENDING"` |
| **Actual Output** | |
| **Justification** | Per spec, WALLET also starts as PENDING. |

### TC-CHKOUT-07 — GST is exactly 5%
| Field | Detail |
|---|---|
| **Input** | Checkout, compare `cart_total * 1.05` to `order_total` |
| **Expected Output** | `order_total ≈ cart_total * 1.05` |
| **Actual Output** | |
| **Justification** | Tax compliance — GST must be applied once at exactly 5%. |

### TC-CHKOUT-08 — COD rejected above 5000
| Field | Detail |
|---|---|
| **Input** | Add 100 units of most expensive product, checkout with COD |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | The spec explicitly prohibits COD for orders exceeding ₹5000. |

### TC-CHKOUT-09 — Cart empty after successful checkout
| Field | Detail |
|---|---|
| **Input** | Checkout, then `GET /cart` |
| **Expected Output** | Cart `items` array is empty |
| **Actual Output** | |
| **Justification** | Cart must be cleared on order creation to prevent double-ordering. |

---

## 9. Wallet (`test_wallet.py`)

### TC-WALL-01 through TC-WALL-12
All wallet tests passed. Key cases:

| TC | Input | Expected | Result |
|---|---|---|---|
| TC-WALL-01 | `GET /wallet` | `200`, has `wallet_balance` | |
| TC-WALL-02 | Add `amount: 100` | `200 OK` | |
| TC-WALL-03 | Add `amount: 0` | `400` | |
| TC-WALL-04 | Add `amount: -50` | `400` | |
| TC-WALL-05 | Add `amount: 100000` (boundary) | `200 OK` | |
| TC-WALL-06 | Add `amount: 100001` | `400` | |
| TC-WALL-07 | Add 500; verify balance increases by 500 | Balance matches | |
| TC-WALL-08 | Pay `amount: 100` with sufficient balance | `200 OK` | |
| TC-WALL-09 | Pay `amount: 0` | `400` | |
| TC-WALL-10 | Pay `amount: -1` | `400` | |
| TC-WALL-11 | Pay more than balance | `400` | |
| TC-WALL-12 | Pay 200; verify exactly 200 deducted | Balance decreases by exactly 200 | |

---

## 10. Loyalty Points (`test_loyalty.py`)

All loyalty tests passed.

| TC | Input | Expected | Result |
|---|---|---|---|
| TC-LOY-01 | `GET /loyalty` | `200`, has `loyalty_points` | |
| TC-LOY-02 | Redeem `points: 0` | `400` | |
| TC-LOY-03 | Redeem `points: -1` | `400` | |
| TC-LOY-04 | Redeem more than available | `400` | |
| TC-LOY-05 | Redeem 1 point (if available) | `200 OK` | |

---

## 11. Orders (`test_orders.py`)

### TC-ORD-01 — Get all orders
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/orders` |
| **Expected Output** | `200 OK`, array |
| **Actual Output** | |

### TC-ORD-02 — Get order by ID
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/orders/{id}` |
| **Expected Output** | `200 OK` |
| **Actual Output** | |

### TC-ORD-03 — Non-existent order returns 404
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/orders/9999999` |
| **Expected Output** | `404` |
| **Actual Output** | |

### TC-ORD-04 — Cancel order
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/orders/{id}/cancel` on fresh order |
| **Expected Output** | `200`/`204` |
| **Actual Output** | |

### TC-ORD-05 — Cancel non-existent order returns 404
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/orders/9999999/cancel` |
| **Expected Output** | `404` |
| **Actual Output** | |

### TC-ORD-06 — Cancel delivered order returns 400
| Field | Detail |
|---|---|
| **Input** | Cancel an order with `order_status: "DELIVERED"` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | Delivered orders are final; cancellation must be blocked. |

### TC-ORD-07 — Cancel restores product stock
| Field | Detail |
|---|---|
| **Input** | Place order for qty 1, cancel, check stock |
| **Expected Output** | Stock returns to pre-order level |
| **Actual Output** | |
| **Justification** | Inventory management: cancelled items must return to pool. |

### TC-ORD-08 — Invoice contains required fields
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/orders/{id}/invoice` |
| **Expected Output** | Response includes `subtotal`, `gst_amount`, `total_amount` |
| **Actual Output** | |

### TC-ORD-09 — Invoice total matches order total
| Field | Detail |
|---|---|
| **Input** | Compare invoice total to order total |
| **Expected Output** | Values match within 0.01 |
| **Actual Output** | |

### TC-ORD-10 — Invoice GST is 5% of subtotal
| Field | Detail |
|---|---|
| **Input** | Verify `gst_amount == subtotal * 0.05` |
| **Expected Output** | Match within 0.01 |
| **Actual Output** | |

---

## 12. Reviews (`test_reviews.py`)

### TC-REV-01 through TC-REV-14
Most pass. Key failures:

| TC | Input | Expected | Result |
|---|---|---|---|
| TC-REV-01 | `GET /products/{id}/reviews` | `200`, `reviews` array | |
| TC-REV-02–04 | Rating 1, 4, 5 | `200`/`201` | |
| TC-REV-05 | Rating 0 | `400` | |
| TC-REV-06 | Rating 6 | `400` | |
| TC-REV-07 | Rating -1 | `400` | |
| TC-REV-08 | Empty comment | `400` | |
| TC-REV-09 | Comment 201 chars | `400` | |
| TC-REV-10 | Comment 200 chars | `200`/`201` | |
| TC-REV-11 | Post 3-star and 4-star reviews; check `average_rating` | Decimal avg (3.5) | **BUG — returns floored integer** |
| TC-REV-12 | Product with no reviews | `average_rating == 0` | |
| TC-REV-13 | Missing comment field | `400` | |
| TC-REV-14 | Decimal rating (4.5) | `400` | |

---

## 13. Support Tickets (`test_support.py`)

### TC-SUP-01 — Create valid ticket
| Field | Detail |
|---|---|
| **Input** | `POST /api/v1/support/ticket`, valid subject + message |
| **Expected Output** | `200`/`201` |
| **Actual Output** | |

### TC-SUP-02 — New ticket status is OPEN
| Field | Detail |
|---|---|
| **Input** | Create ticket, check `status` field |
| **Expected Output** | `status: "OPEN"` |
| **Actual Output** | |

### TC-SUP-03 — Subject too short (2 chars)
| Field | Detail |
|---|---|
| **Input** | `{"subject": "Hi", ...}` |
| **Expected Output** | `400` |
| **Actual Output** | |

### TC-SUP-04 — Subject exactly 5 chars
| Field | Detail |
|---|---|
| **Input** | `{"subject": "Hello", ...}` |
| **Expected Output** | `200`/`201` |
| **Actual Output** | |

### TC-SUP-05 — Subject too long (101 chars)
| Field | Detail |
|---|---|
| **Input** | `{"subject": "A"*101, ...}` |
| **Expected Output** | `400` |
| **Actual Output** | |

### TC-SUP-06 — Subject exactly 100 chars
| Field | Detail |
|---|---|
| **Input** | `{"subject": "A"*100, ...}` |
| **Expected Output** | `200`/`201` |
| **Actual Output** | |

### TC-SUP-07 — Empty message
| Field | Detail |
|---|---|
| **Input** | `{"message": ""}` |
| **Expected Output** | `400` |
| **Actual Output** | |

### TC-SUP-08 — Message too long (501 chars)
| Field | Detail |
|---|---|
| **Input** | `{"message": "A"*501}` |
| **Expected Output** | `400` |
| **Actual Output** | |

### TC-SUP-09 — Message exactly 500 chars
| Field | Detail |
|---|---|
| **Input** | `{"message": "A"*500}` |
| **Expected Output** | `200`/`201` |
| **Actual Output** | |

### TC-SUP-10 — Message stored exactly
| Field | Detail |
|---|---|
| **Input** | Create ticket; fetch ticket list; verify `message` field |
| **Expected Output** | `message == original` |
| **Actual Output** | `None == "Exact message: ..."` **BUG — message not returned in list** |
| **Justification** | The spec says the full message must be saved exactly; the list endpoint omits the `message` field entirely. |

### TC-SUP-11 — Get all tickets
| Field | Detail |
|---|---|
| **Input** | `GET /api/v1/support/tickets` |
| **Expected Output** | `200 OK`, array |
| **Actual Output** | |

### TC-SUP-12 — OPEN → IN_PROGRESS
| Field | Detail |
|---|---|
| **Input** | `PUT /support/tickets/{id}`, `{"status": "IN_PROGRESS"}` |
| **Expected Output** | `200 OK` |
| **Actual Output** | |

### TC-SUP-13 — IN_PROGRESS → CLOSED
| Field | Detail |
|---|---|
| **Input** | `PUT /support/tickets/{id}`, `{"status": "CLOSED"}` after IN_PROGRESS |
| **Expected Output** | `200 OK` |
| **Actual Output** | |

### TC-SUP-14 — OPEN → CLOSED (skip) is invalid
| Field | Detail |
|---|---|
| **Input** | `PUT /support/tickets/{id}`, `{"status": "CLOSED"}` directly from OPEN |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | State machine violation: OPEN must go through IN_PROGRESS first. |

### TC-SUP-15 — CLOSED → OPEN (backward) is invalid
| Field | Detail |
|---|---|
| **Input** | `PUT /support/tickets/{id}`, `{"status": "OPEN"}` after CLOSED |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | State transitions are one-directional; backward transitions must be blocked. |

### TC-SUP-16 — IN_PROGRESS → OPEN (backward) is invalid
| Field | Detail |
|---|---|
| **Input** | `PUT /support/tickets/{id}`, `{"status": "OPEN"}` from IN_PROGRESS |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | Same as TC-SUP-15. |

### TC-SUP-17 — Invalid status value
| Field | Detail |
|---|---|
| **Input** | `PUT /support/tickets/{id}`, `{"status": "PENDING"}` |
| **Expected Output** | `400 Bad Request` |
| **Actual Output** | `200 OK` **BUG** |
| **Justification** | PENDING is not a valid ticket status. Any value outside the allowed set must be rejected. |

---

# Bug Report

## BUG-ADDR-01 — Address Creation Rejects Valid 6-Digit Pincode

**Severity:** Critical  
**Endpoint:** `POST /api/v1/addresses`

| Field | Detail |
|---|---|
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/addresses` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1`, `Content-Type: application/json` |
| **Body** | `{"label": "HOME", "street": "123 Main Street", "city": "Hyderabad", "pincode": "500001", "is_default": false}` |
| **Expected** | `201 Created` — all fields are valid per spec (label ∈ {HOME,OFFICE,OTHER}, street 5–100 chars, city 2–50 chars, pincode exactly 6 digits) |
| **Actual** | `400 Bad Request` — server responds with "Invalid pincode" or similar validation error |
| **Impact** | All address creation tests fail as a cascade. `test_create_address_valid_home`, `test_create_address_valid_office`, `test_create_address_valid_other`, all boundary tests for street/city, `test_update_address_street`, `test_delete_address`, and `test_update_address_cannot_change_label_city_pincode` all fail because they depend on first creating a valid address. This is a single root-cause bug producing 13 test failures. |

---

## BUG-ADDR-02 — Pincode Length Not Validated (5 and 7 digits accepted)

**Severity:** High  
**Endpoint:** `POST /api/v1/addresses`

| Field | Detail |
|---|---|
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/addresses` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Body (case A)** | `{"label": "HOME", "street": "123 Main Street", "city": "Hyderabad", "pincode": "50000", "is_default": false}` |
| **Body (case B)** | `{"label": "HOME", "street": "123 Main Street", "city": "Hyderabad", "pincode": "5000011", "is_default": false}` |
| **Expected** | `400 Bad Request` — pincode must be exactly 6 digits |
| **Actual** | `200 OK` — both accepted |
| **Impact** | Invalid pincodes (5 or 7 digits) are silently stored, leading to data integrity issues in delivery and logistics. |

---

## BUG-ADDR-03 — Missing Required Field `pincode` Does Not Return 400

**Severity:** High  
**Endpoint:** `POST /api/v1/addresses`

| Field | Detail |
|---|---|
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/addresses` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Body** | `{"label": "HOME", "street": "123 Main St", "city": "Hyderabad"}` |
| **Expected** | `400 Bad Request` — `pincode` is a required field |
| **Actual** | `200 OK` — request accepted without a pincode |
| **Impact** | Orders may be placed against addresses with no delivery pincode, causing fulfilment failures. |

---

## BUG-AUTH-01 — Non-existent User ID Returns 404 Instead of 400

**Severity:** Medium  
**Endpoint:** `GET /api/v1/profile`

| Field | Detail |
|---|---|
| **Method** | GET |
| **URL** | `http://localhost:8080/api/v1/profile` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 9999999` |
| **Body** | None |
| **Expected** | `400 Bad Request` — the spec states: "If it is missing or invalid, the server returns a 400 error" for `X-User-ID` |
| **Actual** | `404 Not Found` |
| **Impact** | Client code that checks for `400` to detect invalid user IDs will silently fail. Spec compliance is broken. |

---

## BUG-CART-01 — Quantity = 0 Accepted on Cart Add

**Severity:** High  
**Endpoint:** `POST /api/v1/cart/add`

| Field | Detail |
|---|---|
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/cart/add` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Body** | `{"product_id": 1, "quantity": 0}` |
| **Expected** | `400 Bad Request` — spec: "quantity must be at least 1; sending 0 must be rejected" |
| **Actual** | `200 OK` — zero-quantity item silently accepted |
| **Impact** | Cart may contain zero-quantity line items that corrupt subtotal and total calculations. |

---

## BUG-CART-02 — Missing Quantity Field Accepted on Cart Add

**Severity:** High  
**Endpoint:** `POST /api/v1/cart/add`

| Field | Detail |
|---|---|
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/cart/add` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Body** | `{"product_id": 1}` |
| **Expected** | `400 Bad Request` — quantity is required |
| **Actual** | `200 OK` — item added with undefined/null quantity |
| **Impact** | A cart item with no quantity would cause undefined behavior in subtotal math and checkout. |

---

## BUG-CART-03 — Subtotal Computed Incorrectly (Negative Value)

**Severity:** Critical  
**Endpoint:** `GET /api/v1/cart`

| Field | Detail |
|---|---|
| **Method** | GET |
| **URL** | `http://localhost:8080/api/v1/cart` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Precondition** | Added product ID 1 with quantity 2; product price is ₹120 |
| **Expected** | `subtotal = 2 * 120 = 240` |
| **Actual** | `subtotal = -16` (negative value) |
| **Impact** | Cart subtotals are severely corrupted. The negative subtotal (-16) instead of 240 suggests the server is using a wrong data type, bit overflow, or wrong field for the calculation. Any checkout based on this total will charge an incorrect amount. This is a critical financial calculation bug. |

---

## BUG-CART-04 — Cart Total Computed Incorrectly

**Severity:** Critical  
**Endpoint:** `GET /api/v1/cart`

| Field | Detail |
|---|---|
| **Method** | GET |
| **URL** | `http://localhost:8080/api/v1/cart` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Precondition** | Cart has items with subtotal = -16 (due to BUG-CART-03) |
| **Expected** | `total = sum of all subtotals = 240` |
| **Actual** | `total = 0` while `sum(subtotals) = -16` |
| **Impact** | The cart total is independently wrong from the subtotals, indicating two separate calculation errors. Checkout will use an incorrect total, leading to wrong order amounts and incorrect GST calculations. |

---

## BUG-CHKOUT-01 — Checkout Succeeds with Empty Cart

**Severity:** High  
**Endpoint:** `POST /api/v1/checkout`

| Field | Detail |
|---|---|
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/checkout` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Body** | `{"payment_method": "COD"}` |
| **Precondition** | Cart is empty (cleared via `DELETE /cart/clear`) |
| **Expected** | `400 Bad Request` — spec: "The cart must not be empty. If it is empty, the server returns a 400 error." |
| **Actual** | `200 OK` — an order is created with no items |
| **Impact** | Ghost orders with no items are created and persisted in the database, corrupting order history and potentially triggering downstream fulfilment processes for empty orders. |

---

## BUG-CHKOUT-02 — COD Allowed Above ₹5000

**Severity:** High  
**Endpoint:** `POST /api/v1/checkout`

| Field | Detail |
|---|---|
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/checkout` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Body** | `{"payment_method": "COD"}` |
| **Precondition** | Cart contains 100 units of the most expensive product, total > ₹5000 |
| **Expected** | `400 Bad Request` — spec: "COD is not allowed if the order total is more than 5000" |
| **Actual** | `200 OK` — COD order created despite exceeding the ₹5000 limit |
| **Impact** | High-value cash deliveries are financially risky for the business. This bypass removes a critical risk-control safeguard. |

---

## BUG-COUP-01 — FIXED Coupon Apply Fails Despite Valid Cart

**Severity:** High  
**Endpoint:** `POST /api/v1/coupon/apply`

| Field | Detail |
|---|---|
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/coupon/apply` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Body** | `{"coupon_code": "<valid_fixed_coupon_code>"}` |
| **Precondition** | Cart total exceeds the coupon's `min_cart_value` |
| **Expected** | `200 OK`, cart total reduced by `discount_value` |
| **Actual** | `400 Bad Request` — coupon rejected despite meeting all conditions |
| **Impact** | Valid promotional discounts cannot be applied. Users who have valid coupon codes cannot redeem them, directly impacting customer experience and potentially revenue. |

---

## BUG-COUP-02 — PERCENT Coupon Response Uses `coupon_code` Key, Not `code`

**Severity:** Medium  
**Endpoint:** `GET /api/v1/admin/coupons` + `POST /api/v1/coupon/apply`

| Field | Detail |
|---|---|
| **Method** | GET then POST |
| **URL** | `http://localhost:8080/api/v1/admin/coupons` |
| **Headers** | `X-Roll-Number: 2024101146` |
| **Expected** | Admin coupons response includes a `code` field per standard API naming |
| **Actual** | `KeyError: 'code'` — the coupon object uses key `coupon_code`, not `code`. The `POST /coupon/apply` body field also needs investigation for whether it accepts `code` or `coupon_code`. |
| **Impact** | API field naming is inconsistent across endpoints, making it impossible to apply coupons programmatically without guessing field names. |

---

## BUG-ORD-01 — Delivered Order Can Be Cancelled

**Severity:** High  
**Endpoint:** `POST /api/v1/orders/{order_id}/cancel`

| Field | Detail |
|---|---|
| **Method** | POST |
| **URL** | `http://localhost:8080/api/v1/orders/{order_id}/cancel` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Body** | `{}` |
| **Precondition** | `order_status` of the target order is `"DELIVERED"` |
| **Expected** | `400 Bad Request` — spec: "A delivered order cannot be cancelled." |
| **Actual** | `200 OK` — order status changed despite being delivered |
| **Impact** | Users can cancel already-delivered orders, potentially triggering fraudulent refunds or corrupting inventory (since the spec requires stock to be restored on cancellation). |

---

## BUG-PROF-01 — Phone with Letters Accepted

**Severity:** Medium  
**Endpoint:** `PUT /api/v1/profile`

| Field | Detail |
|---|---|
| **Method** | PUT |
| **URL** | `http://localhost:8080/api/v1/profile` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Body** | `{"name": "Test User", "phone": "98765abcde"}` |
| **Expected** | `400 Bad Request` — spec: "phone number must be exactly 10 digits" (digits, not characters) |
| **Actual** | `200 OK` — profile updated with alphanumeric phone number |
| **Impact** | Non-numeric phone numbers are stored in the database, breaking any SMS/OTP systems that rely on a numeric phone field, and violating data integrity constraints. |

---

## BUG-REV-01 — Average Rating Is Integer-Floored Instead of Decimal

**Severity:** Medium  
**Endpoint:** `GET /api/v1/products/{product_id}/reviews`

| Field | Detail |
|---|---|
| **Method** | GET |
| **URL** | `http://localhost:8080/api/v1/products/{product_id}/reviews` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Precondition** | Product has multiple reviews including ratings that produce a non-integer average (e.g., mix of 3-star and 4-star reviews with existing reviews) |
| **Expected** | `average_rating` is a decimal (e.g., `3.5` for a 3+4 average) |
| **Actual** | `average_rating = 3` — the value is floored to an integer (test observed `abs(3 - 3.27) = 0.27 > 0.1`) |
| **Impact** | Rating precision is lost. A product with 3 ratings of 5, 5, 3 would show `4` instead of `4.33`, misleading customers about product quality. The spec explicitly states: "The average rating shown must be a proper decimal calculation, not a rounded-down integer." |

---

## BUG-SUP-01 — `message` Field Missing from Ticket List Response

**Severity:** Medium  
**Endpoint:** `GET /api/v1/support/tickets`

| Field | Detail |
|---|---|
| **Method** | GET |
| **URL** | `http://localhost:8080/api/v1/support/tickets` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Expected** | Each ticket object includes `ticket_id`, `subject`, `status`, and `message` |
| **Actual** | Ticket objects only include `ticket_id`, `subject`, `status` — the `message` field is absent |
| **Impact** | Customers cannot see the content of their own support tickets from the list endpoint, making the support ticket system non-functional for message review. |

---

## BUG-SUP-02 — Support Ticket State Machine Not Enforced

**Severity:** High  
**Endpoint:** `PUT /api/v1/support/tickets/{ticket_id}`

| Field | Detail |
|---|---|
| **Method** | PUT |
| **URL** | `http://localhost:8080/api/v1/support/tickets/{ticket_id}` |
| **Headers** | `X-Roll-Number: 2024101146`, `X-User-ID: 1` |
| **Body (case A)** | `{"status": "CLOSED"}` when current status is `OPEN` (skip IN_PROGRESS) |
| **Body (case B)** | `{"status": "OPEN"}` when current status is `CLOSED` (backward transition) |
| **Body (case C)** | `{"status": "OPEN"}` when current status is `IN_PROGRESS` (backward transition) |
| **Body (case D)** | `{"status": "PENDING"}` (invalid status value) |
| **Expected** | `400 Bad Request` for all four cases — spec: "Status can only move in one direction: OPEN → IN_PROGRESS → CLOSED. No other changes are allowed." |
| **Actual** | `200 OK` for all four cases — any status value is accepted regardless of current state |
| **Impact** | The entire support ticket lifecycle is broken. Tickets can jump directly to CLOSED without agent review, be reopened after resolution, and accept entirely invalid status strings. This renders the support workflow non-functional for operational use. |
