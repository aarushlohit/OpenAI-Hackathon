import unittest

from app.events.trace_context import TraceContext


class TraceContextTests(unittest.TestCase):
    def test_child_preserves_trace_id(self) -> None:
        parent = TraceContext()
        child = parent.child()

        self.assertEqual(parent.trace_id, child.trace_id)
        self.assertEqual(parent.span_id, child.parent_span_id)

