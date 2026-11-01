from werkzeug.security import check_password_hash

from database.db import get_user_by_email
from tests.conftest import count_users

VALID = {"name": "Asha Rao", "email": "asha@example.com", "password": "secret123"}


def test_register_page_renders(client):
    resp = client.get("/register")
    assert resp.status_code == 200
    assert b"Create your account" in resp.data


def test_valid_registration_creates_hashed_user_and_redirects(client):
    resp = client.post("/register", data=VALID)

    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    user = get_user_by_email("asha@example.com")
    assert user is not None
    assert user["name"] == "Asha Rao"
    assert user["password_hash"] != "secret123"
    assert check_password_hash(user["password_hash"], "secret123")


def test_success_flash_shown_on_login_page(client):
    resp = client.post("/register", data=VALID, follow_redirects=True)
    assert resp.status_code == 200
    assert "Account created — please sign in" in resp.get_data(as_text=True)
    assert b"auth-success" in resp.data


def test_email_is_normalised(client):
    client.post("/register", data={**VALID, "email": "  Asha@Example.COM "})
    assert get_user_by_email("asha@example.com") is not None


def test_duplicate_email_rejected_case_insensitively(client):
    before = count_users()
    resp = client.post(
        "/register",
        data={"name": "Someone", "email": "DEMO@Spendly.com ", "password": "password123"},
    )
    assert resp.status_code == 400
    assert b"An account with that email already exists" in resp.data
    assert count_users() == before


def test_short_password_rejected(client):
    before = count_users()
    resp = client.post("/register", data={**VALID, "password": "short7!"})
    assert resp.status_code == 400
    assert b"at least 8 characters" in resp.data
    assert count_users() == before


def test_missing_fields_rejected(client):
    before = count_users()
    for field in ("name", "email", "password"):
        resp = client.post("/register", data={**VALID, field: "   " if field != "password" else ""})
        assert resp.status_code == 400, field
        assert b"All fields are required." in resp.data
    assert count_users() == before


def test_invalid_email_rejected(client):
    resp = client.post("/register", data={**VALID, "email": "not-an-email"})
    assert resp.status_code == 400
    assert b"valid email" in resp.data


def test_error_rerender_keeps_name_and_email_but_not_password(client):
    resp = client.post("/register", data={**VALID, "password": "short"})
    html = resp.get_data(as_text=True)
    assert 'value="Asha Rao"' in html
    assert 'value="asha@example.com"' in html
    assert "short" not in html.split('id="password"')[1].split(">")[0]
