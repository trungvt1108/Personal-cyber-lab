"""Pure request-handler tests; no listener or live network is created."""

import pytest

from cyberlab.demo import response_for


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/health",
        "/api/status",
        "/login-demo",
        "/admin-test",
        "/security-test",
        "/scanner-test",
    ],
)
def test_harmless_endpoints(path):
    assert response_for("GET", path)[0] == 200


def test_login_always_rejects():
    status, body = response_for("POST", "/login-demo", 20)
    assert status == 401
    assert body["authenticated"] is False


def test_inputs_are_not_echoed():
    assert "dummy_token" not in str(response_for("GET", "/health?dummy_token=example"))
    assert response_for("GET", "/does-not-exist")[0] == 404


def test_body_and_method_limits():
    assert response_for("POST", "/login-demo", 1025)[0] == 413
    assert response_for("POST", "/login-demo", -1)[0] == 400
    assert response_for("DELETE", "/")[0] == 405
    assert response_for("GET", "http://[invalid/")[0] == 400
