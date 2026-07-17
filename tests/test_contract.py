from copy import deepcopy
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

    def test_contract_declares_canonical_scene_boundary_schema(self):
        schema = self.contract["fieldSchemas"]["scene_boundaries"]
        self.assertEqual("array", schema["type"])
        self.assertEqual(
            ["id", "start_line", "end_line"], schema["items"]["required"]
        )

    def test_contract_declares_full_run_unicode_code_point_limit(self):
        self.assertEqual(
            60000, self.contract["inputBudget"]["maxScriptUnicodeCodePoints"]
        )

    def test_missing_required_root_key_is_invalid(self):
        contract = deepcopy(self.contract)
        del contract["stages"]
        self.assertIn(
            "missing required root key: stages", validate_contract(contract)
        )

    def test_non_list_stage_requires_is_invalid(self):
        contract = deepcopy(self.contract)
        contract["stages"]["stage2"]["requires"] = "scene_count"
        self.assertIn(
            "stage2 requires must be a list of strings", validate_contract(contract)
        )

    def test_non_list_stage_produces_is_invalid(self):
        contract = deepcopy(self.contract)
        contract["stages"]["stage2"]["produces"] = "scene_boundaries"
        self.assertIn(
            "stage2 produces must be a list of strings", validate_contract(contract)
        )

    def test_wrong_unicode_code_point_limit_is_invalid(self):
        contract = deepcopy(self.contract)
        contract["inputBudget"]["maxScriptUnicodeCodePoints"] = 59999
        self.assertIn(
            "inputBudget.maxScriptUnicodeCodePoints must equal 60000",
            validate_contract(contract),
        )

    def test_incomplete_scoring_rule_set_is_invalid(self):
        contract = deepcopy(self.contract)
        del contract["scoring"]["ruleWeights"]["R1.1"]
        self.assertIn(
            "ruleWeights must contain the exact scoring rule set",
            validate_contract(contract),
        )

    def test_wrong_non_scoring_rules_and_hard_gates_are_invalid(self):
        contract = deepcopy(self.contract)
        contract["scoring"]["nonScoringRules"].pop()
        contract["scoring"]["hardGates"].pop()
        errors = validate_contract(contract)
        self.assertIn(
            "nonScoringRules must contain the exact non-scoring rule set", errors
        )
        self.assertIn("hardGates must contain the exact hard gate set", errors)


if __name__ == "__main__":
    unittest.main()
