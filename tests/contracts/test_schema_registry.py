import unittest

from app.contracts.compatibility import CompatibilityChecker
from app.contracts.schema_registry import SchemaRegistry
from app.events.models import EventName


class SchemaRegistryTests(unittest.TestCase):
    def test_registers_and_validates_schema_hash(self) -> None:
        registry = SchemaRegistry()
        schema = registry.register(EventName.AGENT_PROGRESS, {"message": "str"})

        self.assertTrue(registry.validate(EventName.AGENT_PROGRESS, "1.0", schema.schema_hash))

    def test_detects_removed_fields(self) -> None:
        result = CompatibilityChecker().backward_compatible({"event", "payload"}, {"event"})

        self.assertFalse(result.compatible)

