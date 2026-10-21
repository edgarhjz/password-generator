import string
import unittest
from app import app, generate_password, evaluate_password_strength, SYMBOLS


class TestPasswordGenerator(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_generate_password_exact_length_and_pools(self):
        for length in (4, 8, 16, 64, 128):
            pwd = generate_password(
                length=length,
                use_uppercase=True,
                use_lowercase=True,
                use_numbers=True,
                use_symbols=True,
            )
            self.assertEqual(len(pwd), length)
            self.assertTrue(any(c in string.ascii_uppercase for c in pwd))
            self.assertTrue(any(c in string.ascii_lowercase for c in pwd))
            self.assertTrue(any(c in string.digits for c in pwd))
            self.assertTrue(any(c in SYMBOLS for c in pwd))

    def test_generate_password_bounds_validation(self):
        with self.assertRaisesRegex(ValueError, "between 4 and 128"):
            generate_password(length=3)
        with self.assertRaisesRegex(ValueError, "between 4 and 128"):
            generate_password(length=129)
        with self.assertRaisesRegex(ValueError, "must be an integer"):
            generate_password(length="16")  # type: ignore
        with self.assertRaisesRegex(ValueError, "At least one character type"):
            generate_password(
                length=12,
                use_uppercase=False,
                use_lowercase=False,
                use_numbers=False,
                use_symbols=False,
            )

    def test_evaluate_password_strength_reaches_excellent_length(self):
        result = evaluate_password_strength("Abcdefghij1!")
        self.assertIn("Excellent length", result["feedback"])
        self.assertEqual(result["score"], 5)
        self.assertTrue(result["valid"])

    def test_api_generate_and_validate(self):
        resp = self.client.post(
            "/api/generate",
            json={
                "length": 20,
                "use_uppercase": True,
                "use_lowercase": True,
                "use_numbers": True,
                "use_symbols": True,
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["password"]), 20)
        self.assertEqual(data["validation"]["score"], 5)

    def test_api_rejects_invalid_payloads(self):
        self.assertEqual(
            self.client.post("/api/generate", json={"length": 100000}).status_code,
            400,
        )
        self.assertEqual(
            self.client.post("/api/generate", data="not-json").status_code,
            400,
        )
        self.assertEqual(
            self.client.post("/api/validate", json={"password": "a" * 200}).status_code,
            400,
        )

    def test_health_endpoint(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
