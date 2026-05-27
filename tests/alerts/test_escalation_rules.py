import unittest

from app.autonomous.alerting import EscalationRules


class EscalationRulesTests(unittest.TestCase):
    def test_repeated_entity_escalates(self) -> None:
        escalation = EscalationRules().evaluate("pay@upi", ["INV-1", "INV-2"])

        self.assertIsNotNone(escalation)
        self.assertEqual(escalation.event, "escalation_triggered")

