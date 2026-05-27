import unittest

from app.runtime import RuntimeHealthManager


class RuntimeHealthTests(unittest.IsolatedAsyncioTestCase):
    async def test_health_is_ok(self) -> None:
        health = await RuntimeHealthManager().health()

        self.assertEqual(health.status, "ok")

