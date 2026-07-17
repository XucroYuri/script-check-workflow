import json
import unittest
from pathlib import Path

from scripts.contract import load_contract, validate_contract


ROOT = Path(__file__).resolve().parents[1]


class WorkflowContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract(ROOT / "contracts/workflow-contract.json")

    def test_contract_has_no_validation_errors(self):
        self.assertEqual([], validate_contract(self.contract))

    def test_continuity_inputs_have_explicit_producers(self):
        stages = self.contract["stages"]
        self.assertIn("scene_boundaries", stages["stage2"]["produces"])
        self.assertIn("scene_shot_map", stages["stage3"]["produces"])
        self.assertIn("key_action_events", stages["stage4"]["produces"])

    def test_scoring_weights_total_one_hundred(self):
        total = sum(self.contract["scoring"]["ruleWeights"].values())
        self.assertEqual(100.0, total)

    def test_every_rule_is_scoring_or_explicitly_non_scoring(self):
        scoring = set(self.contract["scoring"]["ruleWeights"])
        non_scoring = set(self.contract["scoring"]["nonScoringRules"])
        self.assertTrue(scoring.isdisjoint(non_scoring))
        self.assertEqual(42, len(scoring | non_scoring))


if __name__ == "__main__":
    unittest.main()
