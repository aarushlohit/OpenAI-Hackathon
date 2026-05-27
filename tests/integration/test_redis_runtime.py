import unittest

from app.runtime.redis_runtime import RedisRuntime


class FakeRedis:
    def __init__(self) -> None:
        self.published = []

    async def ping(self):
        return True

    async def publish(self, channel, payload):
        self.published.append((channel, payload))
        return 1


class RedisRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_publish_requires_namespaced_channels(self) -> None:
        runtime = RedisRuntime(FakeRedis())

        count = await runtime.publish("hermes:investigation:test", "{}")

        self.assertEqual(count, 1)
        with self.assertRaises(ValueError):
            await runtime.publish("foreign:test", "{}")

    async def test_ping_reports_degraded_without_client(self) -> None:
        status = await RedisRuntime().ping()

        self.assertFalse(status.reachable)
        self.assertIn("not configured", status.detail)


if __name__ == "__main__":
    unittest.main()

