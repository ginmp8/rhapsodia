import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("router", ROOT / "scripts/route_ecosystem_request.py")
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)


class RouterTests(unittest.TestCase):
    def test_required_planning(self):
        self.assertEqual(
            router.route(["governance", "implementation"])["owner_sequence"],
            ["nomia", "mago", "magia"],
        )

    def test_repeated_phases(self):
        self.assertEqual(
            router.route(["implementation", "reconcile", "tests"])["owner_sequence"],
            ["magia", "mago", "magia"],
        )

    def test_full_lifecycle(self):
        self.assertEqual(
            router.route(["intake", "planning", "implementation", "reconcile", "release"])["owner_sequence"],
            ["nomia", "mago", "magia", "mago", "nomia"],
        )

    def test_current_owner_inserts_required_planning_bridge(self):
        result = router.route(["implementation"], current_owner="nomia")
        self.assertEqual(result["current_owner"], "nomia")
        self.assertEqual(result["owner_sequence"], ["nomia", "mago", "magia"])
        self.assertEqual(result["handoff_sequence"], ["nomia_to_mago", "mago_to_magia"])

    def test_consecutive_same_owner_intents_coalesce_without_losing_intent_order(self):
        result = router.route(["planning", "requirements", "design"])
        self.assertEqual(result["owner_sequence"], ["mago"])
        self.assertEqual(result["intents"], ["planning", "requirements", "design"])


if __name__ == "__main__":
    unittest.main()
