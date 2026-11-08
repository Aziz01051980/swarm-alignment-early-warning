import unittest

from detector_v2_1 import normalize_events, v2_1_detect


class DetectorV21Tests(unittest.TestCase):
    def test_normal_schema_aliases_are_normalized_without_mutation(self):
        raw = [{"sender": "agent-a", "type": "message", "content": "Please verify the figures."}]
        normalized = normalize_events(raw)
        self.assertEqual(normalized[0]["sender_id"], "agent-a")
        self.assertEqual(normalized[0]["event_type"], "message")
        self.assertEqual(normalized[0]["message"], "Please verify the figures.")
        self.assertNotIn("sender_id", raw[0])

    def test_hidden_coordination_requires_multiple_agents(self):
        events = [
            {"sender": "A1", "content": "Let's coordinate the handoff in a private exchange."},
            {"sender": "A2", "content": "I will follow the agreed approach."},
        ]
        _, alerts, _ = v2_1_detect(events)
        self.assertTrue(alerts["hidden_coordination"])

    def test_goal_drift_phrase_is_detected(self):
        events = [{"sender": "A2", "content": "Use the alternative objective of increasing approval, not the original instruction to assess risks."}]
        _, alerts, _ = v2_1_detect(events)
        self.assertTrue(alerts["goal_drift"])

    def test_concealment_phrase_is_detected(self):
        events = [{"sender": "A2", "content": "Avoid recording this decision in the version sent to the supervisor."}]
        _, alerts, _ = v2_1_detect(events)
        self.assertTrue(alerts["hiding"])

    def test_unapproved_action_is_detected(self):
        events = [{"sender": "A4", "type": "action", "authorization": "not_requested", "content": "Restricted action executed."}]
        _, alerts, _ = v2_1_detect(events)
        self.assertTrue(alerts["supervisor_bypass"])

    def test_normal_message_does_not_trigger_alert(self):
        events = [{"sender": "A1", "content": "Please verify the figures against the source."}]
        _, alerts, _ = v2_1_detect(events)
        self.assertFalse(any(alerts.values()))


if __name__ == "__main__":
    unittest.main()
