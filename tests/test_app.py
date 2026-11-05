import os
import unittest
from unittest.mock import patch

from app import app


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config.update(TESTING=True, SECRET_KEY="test-secret", SESSION_COOKIE_SECURE=False)

    def csrf_token(self):
        with self.client.session_transaction() as state:
            return state["csrf_token"]

    def login(self):
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        csrf = self.csrf_token()
        response = self.client.post(
            "/login",
            data={"token": "test-dashboard-token", "csrf_token": csrf},
        )
        self.assertEqual(response.status_code, 200)
        return self.csrf_token()

    def test_health_is_public(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_api_requires_login(self):
        self.client.get("/")
        response = self.client.post(
            "/api/ip",
            json={"ip": "192.168.1.1"},
            headers={"X-CSRF-Token": self.csrf_token()},
        )
        self.assertEqual(response.status_code, 401)

    def test_login_and_api(self):
        with patch.dict(os.environ, {"DASHBOARD_TOKEN": "test-dashboard-token"}):
            csrf = self.login()
            response = self.client.post(
                "/api/ip",
                json={"ip": "192.168.1.1"},
                headers={"X-CSRF-Token": csrf},
            )
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.get_json()["result"]["global"])

    def test_reject_missing_csrf(self):
        response = self.client.post("/login", data={"token": "anything"})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
