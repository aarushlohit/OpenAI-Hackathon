import unittest

from app.events.dead_letter_queue import DeadLetterEvent, DeadLetterQueue


class DeadLetterQueueTests(unittest.IsolatedAsyncioTestCase):
    async def test_quarantines_events(self) -> None:
        queue = DeadLetterQueue(max_size=2)

        await queue.quarantine(DeadLetterEvent(reason="invalid_schema"))

        self.assertEqual(len(await queue.list()), 1)

