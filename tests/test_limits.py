import unittest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from billg.util.network import limits, rate_limit_storage

app = FastAPI()


@app.get("/limited")
@limits(calls=2, period_seconds=3)
async def limited_endpoint(request: Request):
    return {"message": "ok"}


client = TestClient(app)


class TestLimitsDecorator(unittest.TestCase):
    def setUp(self):
        rate_limit_storage.clear()

    def test_limits_decorator_respects_limit(self):
        response1 = client.get("/limited")
        self.assertEqual(response1.status_code, 200)
        response2 = client.get("/limited")
        self.assertEqual(response2.status_code, 200)
        response3 = client.get("/limited")
        self.assertEqual(response3.status_code, 429)
        self.assertIn("Rate limit exceeded", response3.json()["detail"])

    def test_limits_decorator_resets_after_period(self):
        response1 = client.get("/limited")
        self.assertEqual(response1.status_code, 200)
        response2 = client.get("/limited")
        self.assertEqual(response2.status_code, 200)
        key = f"testclient:limited_endpoint"
        if key in rate_limit_storage:
            call_count, last_reset = rate_limit_storage[key]
            rate_limit_storage[key] = (call_count, last_reset - 4)
        response3 = client.get("/limited")
        self.assertEqual(response3.status_code, 200)


if __name__ == "__main__":
    unittest.main()
