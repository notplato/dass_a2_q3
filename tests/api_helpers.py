# api_helpers.py
import requests

BASE_URL = "http://localhost:8080/api/v1"
ROLL_NUMBER = "2024101146"

def headers(user_id=None):
    h = {"X-Roll-Number": ROLL_NUMBER}
    if user_id is not None:
        h["X-User-ID"] = str(user_id)
    return h

def get(path, user_id=None, extra_headers=None):
    h = headers(user_id)
    if extra_headers:
        h.update(extra_headers)
    return requests.get(f"{BASE_URL}{path}", headers=h)

def post(path, body=None, user_id=None, extra_headers=None):
    h = headers(user_id)
    if extra_headers:
        h.update(extra_headers)
    return requests.post(f"{BASE_URL}{path}", json=body, headers=h)

def put(path, body=None, user_id=None, extra_headers=None):
    h = headers(user_id)
    if extra_headers:
        h.update(extra_headers)
    return requests.put(f"{BASE_URL}{path}", json=body, headers=h)

def delete(path, user_id=None, extra_headers=None):
    h = headers(user_id)
    if extra_headers:
        h.update(extra_headers)
    return requests.delete(f"{BASE_URL}{path}", headers=h)

